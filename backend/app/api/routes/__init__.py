"""API routes package."""

from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.events import router as events_router
from app.api.routes.exports import router as exports_router
from app.api.routes.findings import router as findings_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.reviews import router as reviews_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(reviews_router, prefix="/api", tags=["Reviews"])
api_router.include_router(findings_router, prefix="/api", tags=["Findings"])
api_router.include_router(events_router, prefix="/api", tags=["Events"])
api_router.include_router(history_router, prefix="/api", tags=["History"])
api_router.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
api_router.include_router(exports_router, prefix="/api", tags=["Exports"])
