"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.security import UserInfo, get_current_user

router = APIRouter()


@router.get("/auth/me")
async def get_current_user_profile(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
) -> dict:
    """Get the current authenticated user's profile.

    Returns user information extracted from the JWT token.
    """
    return {
        "userId": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "tenantId": current_user.tenant_id,
        "roles": current_user.roles,
    }
