"""User and token models for authentication."""

from dataclasses import dataclass
from typing import Any


@dataclass
class UserInfo:
    """Authenticated user information extracted from JWT token."""

    user_id: str  # oid claim (Object ID)
    email: str  # preferred_username or email claim
    name: str  # name claim
    tenant_id: str  # tid claim
    roles: list[str]  # roles claim (if present)
    raw_claims: dict[str, Any]  # All token claims

    @classmethod
    def from_token_claims(cls, claims: dict[str, Any]) -> "UserInfo":
        """Create UserInfo from decoded JWT claims."""
        return cls(
            user_id=claims.get("oid", claims.get("sub", "")),
            email=claims.get("preferred_username", claims.get("email", "")),
            name=claims.get("name", "Unknown User"),
            tenant_id=claims.get("tid", ""),
            roles=claims.get("roles", []),
            raw_claims=claims,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "userId": self.user_id,
            "email": self.email,
            "name": self.name,
            "tenantId": self.tenant_id,
            "roles": self.roles,
        }
