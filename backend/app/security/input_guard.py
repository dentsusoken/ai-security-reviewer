"""Input validation and sanitization middleware.

This module provides protection against:
- Path traversal attacks
- SQL injection patterns
- XSS payloads
- Command injection
- Oversized payloads
"""

import re
from typing import Any

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Maximum request body size (10MB)
MAX_BODY_SIZE = 10 * 1024 * 1024

# Dangerous patterns to detect
DANGEROUS_PATTERNS = [
    # Path traversal
    (r"\.\./", "path_traversal"),
    (r"\.\.\\", "path_traversal"),
    (r"%2e%2e[/\\]", "path_traversal"),
    # SQL injection indicators
    (r"('|\")\s*(or|and)\s*('|\"|\d)", "sql_injection"),
    (r";\s*(drop|delete|update|insert|alter)\s+", "sql_injection"),
    (r"union\s+(all\s+)?select", "sql_injection"),
    # XSS patterns
    (r"<script[^>]*>", "xss"),
    (r"javascript:", "xss"),
    (r"on(load|error|click|mouseover)=", "xss"),
    # Command injection
    (r"[;&|`$]", "command_injection"),
    (r"\$\(", "command_injection"),
]

# Compiled patterns for efficiency
COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), threat_type)
    for pattern, threat_type in DANGEROUS_PATTERNS
]


class InputValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, threat_type: str, detail: str):
        self.threat_type = threat_type
        self.detail = detail
        super().__init__(detail)


def detect_threats(value: str) -> tuple[bool, str | None]:
    """Check a string value for dangerous patterns.

    Args:
        value: The string to check

    Returns:
        Tuple of (is_threat, threat_type)
    """
    if not isinstance(value, str):
        return False, None

    for pattern, threat_type in COMPILED_PATTERNS:
        if pattern.search(value):
            return True, threat_type

    return False, None


def sanitize_string(value: str) -> str:
    """Sanitize a string by escaping dangerous characters.

    Args:
        value: The string to sanitize

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value

    # HTML entity encoding for XSS prevention
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
    }

    for char, replacement in replacements.items():
        value = value.replace(char, replacement)

    return value


def validate_dict(data: dict[str, Any], path: str = "") -> None:
    """Recursively validate dictionary values for threats.

    Args:
        data: Dictionary to validate
        path: Current path for error reporting

    Raises:
        InputValidationError: If a threat is detected
    """
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key

        if isinstance(value, str):
            is_threat, threat_type = detect_threats(value)
            if is_threat:
                raise InputValidationError(
                    threat_type=threat_type,
                    detail=f"Potentially malicious input detected at '{current_path}'",
                )
        elif isinstance(value, dict):
            validate_dict(value, current_path)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str):
                    is_threat, threat_type = detect_threats(item)
                    if is_threat:
                        raise InputValidationError(
                            threat_type=threat_type,
                            detail=f"Potentially malicious input detected at '{current_path}[{i}]'",
                        )
                elif isinstance(item, dict):
                    validate_dict(item, f"{current_path}[{i}]")


class InputGuardMiddleware(BaseHTTPMiddleware):
    """Middleware that validates and sanitizes incoming requests."""

    async def dispatch(self, request: Request, call_next):
        """Process the request through validation checks."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Request body too large. Maximum size is {MAX_BODY_SIZE} bytes.",
            )

        # Validate query parameters
        for key, value in request.query_params.items():
            is_threat, threat_type = detect_threats(value)
            if is_threat:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Input validation failed",
                        "threat_type": threat_type,
                        "location": f"query.{key}",
                    },
                )

        # Validate path parameters
        for key, value in request.path_params.items():
            if isinstance(value, str):
                is_threat, threat_type = detect_threats(value)
                if is_threat:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Input validation failed",
                            "threat_type": threat_type,
                            "location": f"path.{key}",
                        },
                    )

        # Continue to next middleware/handler
        response = await call_next(request)
        return response


# Export for use in main.py
__all__ = [
    "InputGuardMiddleware",
    "InputValidationError",
    "detect_threats",
    "sanitize_string",
    "validate_dict",
    "MAX_BODY_SIZE",
]
