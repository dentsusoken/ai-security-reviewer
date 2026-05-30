"""Semgrep Azure Function client.

Sends code files to the Semgrep Azure Function for SAST analysis and
returns normalised finding payloads.
"""

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SemgrepClient:
    """Client for invoking the Semgrep Azure Function."""

    def __init__(self) -> None:
        settings = get_settings()
        self.function_url = settings.semgrep_function_url.rstrip("/")
        self.function_key = settings.semgrep_function_key
        self._timeout = 360  # generous timeout for large scans

    @property
    def is_configured(self) -> bool:
        """Return True if the Semgrep function URL is set."""
        return bool(self.function_url)

    async def scan(
        self,
        files: list[dict[str, str]],
        rules: str = "auto",
    ) -> dict[str, Any]:
        """Send code files for Semgrep scanning.

        Args:
            files: List of ``{"path": "...", "content": "..."}`` dicts.
            rules: Semgrep config string (default ``"auto"``).

        Returns:
            Dict with ``findings``, ``errors``, and ``version`` keys.

        Raises:
            SemgrepScanError: When the function returns a non-200 response.
        """
        if not self.is_configured:
            raise SemgrepScanError("Semgrep function URL is not configured")

        url = f"{self.function_url}/api/scan"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.function_key:
            headers["x-functions-key"] = self.function_key

        payload = {"files": files, "rules": rules}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except httpx.TimeoutException:
                raise SemgrepScanError("Semgrep scan timed out") from None
            except httpx.RequestError as exc:
                raise SemgrepScanError(
                    f"Failed to connect to Semgrep function: {exc}"
                ) from exc

        if response.status_code != 200:
            detail = response.text[:500]
            raise SemgrepScanError(
                f"Semgrep function returned {response.status_code}: {detail}"
            )

        return response.json()


class SemgrepScanError(Exception):
    """Raised when a Semgrep scan fails."""


_client: SemgrepClient | None = None


def get_semgrep_client() -> SemgrepClient:
    """Get or create a singleton SemgrepClient."""
    global _client
    if _client is None:
        _client = SemgrepClient()
    return _client
