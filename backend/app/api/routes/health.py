"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
@router.get("/api/health")
def root() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
