import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.observability import CorrelationIdMiddleware, setup_logging
from app.security import InputGuardMiddleware

# Setup structured logging
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logs = os.getenv("LOG_FORMAT", "json").lower() == "json"
setup_logging(level=log_level, json_format=json_logs)

app = FastAPI(
    title=settings.app_name,
    description="AI Security Reviewer API - セキュリティレビュー自動化サービス",
    version="0.1.0",
)

# Add middlewares (order matters - last added is first executed)
# 1. Correlation ID middleware (outermost - runs first)
app.add_middleware(CorrelationIdMiddleware, log_requests=True, log_responses=True)

# 2. Input validation middleware
app.add_middleware(InputGuardMiddleware)

# 3. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)
