"""History endpoint."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query

from app.api.schemas.review import HistoryResponse, HistoryReview
from app.services.review_state import get_review_manager

router = APIRouter()


def parse_period_filter(period: str | None) -> datetime | None:
    """Parse period filter to datetime cutoff."""
    if not period:
        return None

    now = datetime.now(UTC)

    period_map = {
        "today": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "quarter": timedelta(days=90),
    }

    delta = period_map.get(period.lower())
    if delta:
        return now - delta
    return None


def parse_score_range(score_range: str | None) -> tuple[int | None, int | None]:
    """Parse score range filter to min/max values."""
    if not score_range:
        return None, None

    range_map = {
        "0-50": (0, 50),
        "51-70": (51, 70),
        "71-85": (71, 85),
        "86-100": (86, 100),
    }

    return range_map.get(score_range, (None, None))


@router.get("/history", response_model=HistoryResponse)
def get_history(  # noqa: C901
    query: str | None = Query(default=None, description="Search by repo name"),
    period: str | None = Query(default=None, description="Time period filter"),
    score_range: str | None = Query(
        default=None, alias="scoreRange", description="Score range filter"
    ),
    perspective: str | None = Query(default=None, description="Perspective filter"),
) -> HistoryResponse:
    """Get review history with optional filters.

    Returns completed reviews from real review data, with support for filtering.
    """
    manager = get_review_manager()

    # Get all completed reviews (already sorted newest first)
    completed_reviews = manager.get_completed_reviews()

    # Parse filters
    period_cutoff = parse_period_filter(period)
    score_min, score_max = parse_score_range(score_range)

    # Filter and convert reviews
    reviews = []
    for state in completed_reviews:
        review_data = manager.review_to_history_format(state)

        # Apply search filter
        if query:
            repo_url = review_data.get("repoUrl", "")
            if query.lower() not in repo_url.lower():
                continue

        # Apply period filter
        if period_cutoff and state.completed_at:
            # Make state.completed_at timezone-aware if needed
            completed_at = state.completed_at
            if completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=UTC)
            if completed_at < period_cutoff:
                continue

        # Apply score range filter
        if score_min is not None or score_max is not None:
            score = review_data["scoreSummary"]["overall"]
            if score_min is not None and score < score_min:
                continue
            if score_max is not None and score > score_max:
                continue

        # Apply perspective filter
        if perspective:
            perspectives = review_data.get("perspectives", [])
            if perspective not in perspectives:
                continue

        reviews.append(
            HistoryReview(
                id=review_data["id"],
                repoUrl=review_data["repoUrl"],
                branch=review_data["branch"],
                inputType=review_data["inputType"],
                perspectives=review_data["perspectives"],
                startedAt=review_data["startedAt"],
                durationMs=review_data["durationMs"],
                scoreSummary=review_data["scoreSummary"],
            )
        )

    return HistoryResponse(
        reviews=reviews,
        totalCount=len(reviews),
    )
