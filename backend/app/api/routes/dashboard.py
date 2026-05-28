"""Dashboard statistics endpoint."""

from fastapi import APIRouter

from app.api.schemas.review import DashboardStats, HistoryReview
from app.services.review_state import get_review_manager

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats() -> DashboardStats:
    """Get dashboard statistics from real review data."""
    manager = get_review_manager()

    # Get stats from completed reviews
    stats = manager.get_dashboard_stats()

    # Get recent reviews (up to 3, newest first)
    completed_reviews = manager.get_completed_reviews()[:3]

    recent_reviews = [
        HistoryReview(
            id=data["id"],
            repoUrl=data["repoUrl"],
            branch=data["branch"],
            inputType=data["inputType"],
            perspectives=data["perspectives"],
            startedAt=data["startedAt"],
            durationMs=data["durationMs"],
            scoreSummary=data["scoreSummary"],
        )
        for data in [manager.review_to_history_format(r) for r in completed_reviews]
    ]

    return DashboardStats(
        totalReviews=stats["total_reviews"],
        totalFindings=stats["total_findings"],
        resolvedFindings=stats["resolved_findings"],
        averageScore=stats["average_score"],
        recentReviews=recent_reviews,
    )
