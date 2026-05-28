"""JWT authentication middleware for Azure Entra ID tokens."""

import os
from typing import Annotated, Any

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.models import UserInfo

# Entra ID configuration
TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")

# JWKS URL for token validation
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

# Cache for JWKS keys
_jwks_cache: dict[str, Any] | None = None

# Security scheme
security = HTTPBearer(auto_error=False)


class JWTAuthMiddleware:
    """Middleware for JWT token validation (placeholder for future use)."""

    pass


async def get_jwks() -> dict[str, Any]:
    """Fetch and cache JWKS from Entra ID."""
    global _jwks_cache

    if _jwks_cache is not None:
        return _jwks_cache

    if not TENANT_ID:
        # Development mode - return empty
        return {"keys": []}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
        except Exception:
            return {"keys": []}


def decode_token_without_verification(token: str) -> dict[str, Any]:
    """Decode JWT token without verification (for development/testing).

    WARNING: This should only be used in development or when proper
    verification is not possible. In production, use proper JWKS validation.
    """
    import base64
    import json

    try:
        # Split token into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        raise ValueError(f"Failed to decode token: {e}") from e


async def validate_token(token: str) -> dict[str, Any]:
    """Validate JWT token and return claims.

    In production with proper setup, this would verify:
    - Token signature using JWKS
    - Token expiration
    - Issuer and audience claims

    For hackathon MVP, we decode without full cryptographic verification
    but still validate structure and basic claims.
    """
    try:
        claims = decode_token_without_verification(token)

        # Validate required claims exist
        if "oid" not in claims and "sub" not in claims:
            raise ValueError("Missing user identifier claim")

        # Validate audience if CLIENT_ID is configured
        if CLIENT_ID:
            aud = claims.get("aud", "")
            if isinstance(aud, list):
                if CLIENT_ID not in aud:
                    raise ValueError("Invalid audience")
            elif aud != CLIENT_ID:
                raise ValueError("Invalid audience")

        # Validate issuer if TENANT_ID is configured
        if TENANT_ID:
            iss = claims.get("iss", "")
            expected_issuers = [
                f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
                f"https://sts.windows.net/{TENANT_ID}/",
            ]
            if iss not in expected_issuers:
                raise ValueError("Invalid issuer")

        return claims

    except Exception as e:
        raise ValueError(f"Token validation failed: {e}") from e


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UserInfo:
    """Dependency to get the current authenticated user.

    Raises HTTPException 401 if not authenticated.
    """
    # Check for development mode bypass
    if os.getenv("AUTH_DISABLED", "").lower() == "true":
        # Return mock user for development
        return UserInfo(
            user_id="dev-user-001",
            email="dev@example.com",
            name="開発ユーザー",
            tenant_id="dev-tenant",
            roles=["developer"],
            raw_claims={},
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = await validate_token(credentials.credentials)
        return UserInfo.from_token_claims(claims)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"無効なトークン: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UserInfo | None:
    """Dependency to get the current user if authenticated, None otherwise.

    Does not raise exception if not authenticated.
    """
    # Check for development mode bypass
    if os.getenv("AUTH_DISABLED", "").lower() == "true":
        return UserInfo(
            user_id="dev-user-001",
            email="dev@example.com",
            name="開発ユーザー",
            tenant_id="dev-tenant",
            roles=["developer"],
            raw_claims={},
        )

    if credentials is None:
        return None

    try:
        claims = await validate_token(credentials.credentials)
        return UserInfo.from_token_claims(claims)
    except ValueError:
        return None
