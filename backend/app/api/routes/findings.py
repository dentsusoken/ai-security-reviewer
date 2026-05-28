"""Finding endpoints."""

from fastapi import APIRouter, HTTPException

from app.api.schemas.finding import FindingDetail, FindingStatusUpdate
from app.data.mock_data import MOCK_FINDINGS, finding_states

router = APIRouter()


@router.get("/findings/{finding_id}", response_model=FindingDetail)
def get_finding(finding_id: str) -> FindingDetail:
    """Get finding details by ID."""
    finding_data = MOCK_FINDINGS.get(finding_id)

    if finding_data is None:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Use current resolution state from mutable store
    current_state = finding_states.get(finding_id, "open")
    finding_dict = {**finding_data, "resolutionState": current_state}

    return FindingDetail(**finding_dict)


@router.patch("/findings/{finding_id}/status", response_model=FindingDetail)
def update_finding_status(
    finding_id: str,
    update: FindingStatusUpdate,
) -> FindingDetail:
    """Update finding resolution status."""
    finding_data = MOCK_FINDINGS.get(finding_id)

    if finding_data is None:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Update the mutable state
    finding_states[finding_id] = update.resolution_state.value

    # Return updated finding
    finding_dict = {**finding_data, "resolutionState": update.resolution_state.value}
    return FindingDetail(**finding_dict)
