"""Correlation ID and structured logging middleware.

This module provides:
- Correlation ID generation and propagation
- Structured JSON logging
- Request/response logging
- Performance timing
"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Get the current correlation ID from context.

    Returns:
        The current correlation ID or empty string if not set
    """
    return correlation_id_var.get()


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        extra_keys = [
            "method",
            "path",
            "status_code",
            "duration_ms",
            "user_id",
            "client_ip",
            "user_agent",
        ]
        for key in extra_keys:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        # Add any custom extra fields
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_data.update(record.extra_data)

        return json.dumps(log_data, default=str)


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation_id attribute to the record."""
        record.correlation_id = get_correlation_id() or "-"
        return True


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting (True for production)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler with correlation ID filter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler.addFilter(CorrelationIdFilter())

    if json_format:
        handler.setFormatter(StructuredFormatter())
    else:
        # Human-readable format for development
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(handler)

    # Set uvicorn loggers to use our formatter
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with correlation ID filter attached.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    # Add filter if not already present
    if not any(isinstance(f, CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(CorrelationIdFilter())
    return logger


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that manages correlation IDs and request logging."""

    # Headers to check for incoming correlation ID
    CORRELATION_HEADERS = [
        "x-correlation-id",
        "x-request-id",
        "traceparent",
    ]

    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        """Initialize the middleware.

        Args:
            app: The ASGI application
            log_requests: Whether to log incoming requests
            log_responses: Whether to log outgoing responses
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.logger = get_logger("api.access")

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with correlation ID tracking."""
        # Extract or generate correlation ID
        correlation_id = self._get_correlation_id(request)
        correlation_id_var.set(correlation_id)

        # Start timing
        start_time = time.perf_counter()

        # Log incoming request
        if self.log_requests:
            self._log_request(request)

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.error(
                f"Request failed: {e}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": self._get_client_ip(request),
                },
                exc_info=True,
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Log response
        if self.log_responses:
            self._log_response(request, response, duration_ms)

        return response

    def _get_correlation_id(self, request: Request) -> str:
        """Extract correlation ID from request headers or generate new one."""
        for header in self.CORRELATION_HEADERS:
            value = request.headers.get(header)
            if value:
                # For traceparent, extract the trace-id portion
                if header == "traceparent" and "-" in value:
                    parts = value.split("-")
                    if len(parts) >= 2:
                        return parts[1]
                return value

        # Generate new correlation ID
        return str(uuid.uuid4())

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check forwarded headers first (for proxies/load balancers)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _log_request(self, request: Request) -> None:
        """Log incoming request details."""
        self.logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

    def _log_response(
        self, request: Request, response: Response, duration_ms: float
    ) -> None:
        """Log response details."""
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING

        self.logger.log(
            log_level,
            f"Response: {request.method} {request.url.path} -> {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": self._get_client_ip(request),
            },
        )


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    extra_data: dict[str, Any] | None = None,
    **kwargs,
) -> None:
    """Log a message with additional context data.

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        extra_data: Additional data to include in structured log
        **kwargs: Extra arguments passed to logger
    """
    extra = kwargs.pop("extra", {})
    if extra_data:
        extra["extra_data"] = extra_data
    logger.log(level, message, extra=extra, **kwargs)


__all__ = [
    "CorrelationIdMiddleware",
    "StructuredFormatter",
    "correlation_id_var",
    "get_correlation_id",
    "get_logger",
    "log_with_context",
    "setup_logging",
]
