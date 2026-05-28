"""
Findings Repository.

Handles persistence of security findings to Cosmos DB.
Falls back to in-memory storage when Cosmos DB is not configured.
"""

import logging
from datetime import datetime
from typing import Any

from app.services.cosmos_service import get_cosmos_service

logger = logging.getLogger(__name__)

# In-memory storage fallback
_memory_store: dict[str, list[dict[str, Any]]] = {}  # session_id -> findings


class FindingsRepository:
    """Repository for findings persistence."""

    CONTAINER_NAME = "findings"

    def __init__(self) -> None:
        """Initialize repository."""
        self._cosmos_service = None

    async def _ensure_cosmos(self) -> None:
        """Ensure Cosmos DB service is initialized."""
        if self._cosmos_service is None:
            self._cosmos_service = await get_cosmos_service()

    async def create(self, finding_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new finding.

        Args:
            finding_data: Finding data including id, reviewSessionId, etc.

        Returns:
            Created finding data
        """
        await self._ensure_cosmos()

        # Add timestamps
        if "createdAt" not in finding_data:
            finding_data["createdAt"] = datetime.utcnow().isoformat()

        if self._cosmos_service.is_mock_mode:
            session_id = finding_data["reviewSessionId"]
            if session_id not in _memory_store:
                _memory_store[session_id] = []
            _memory_store[session_id].append(finding_data.copy())
            return finding_data

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)
        result = await container.create_item(body=finding_data)
        return result

    async def create_many(
        self, findings: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create multiple findings.

        Args:
            findings: List of finding data

        Returns:
            List of created findings
        """
        results = []
        for finding in findings:
            result = await self.create(finding)
            results.append(result)
        return results

    async def get(
        self, finding_id: str, session_id: str
    ) -> dict[str, Any] | None:
        """Get a finding by ID.

        Args:
            finding_id: Finding ID
            session_id: Review session ID (partition key)

        Returns:
            Finding data or None if not found
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            findings = _memory_store.get(session_id, [])
            for f in findings:
                if f.get("id") == finding_id:
                    return f
            return None

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)
        try:
            result = await container.read_item(
                item=finding_id, partition_key=session_id
            )
            return result
        except Exception:
            return None

    async def list_by_session(
        self,
        session_id: str,
        severity: str | None = None,
        resolution_state: str | None = None,
    ) -> list[dict[str, Any]]:
        """List findings for a review session.

        Args:
            session_id: Review session ID (partition key)
            severity: Filter by severity (optional)
            resolution_state: Filter by resolution state (optional)

        Returns:
            List of findings
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            findings = _memory_store.get(session_id, [])
            if severity:
                findings = [f for f in findings if f.get("severity") == severity]
            if resolution_state:
                findings = [
                    f
                    for f in findings
                    if f.get("resolutionState") == resolution_state
                ]
            # Sort by severity order
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            findings.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 4))
            return findings

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        conditions = ["c.reviewSessionId = @sessionId"]
        params = [{"name": "@sessionId", "value": session_id}]

        if severity:
            conditions.append("c.severity = @severity")
            params.append({"name": "@severity", "value": severity})

        if resolution_state:
            conditions.append("c.resolutionState = @resolutionState")
            params.append({"name": "@resolutionState", "value": resolution_state})

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT * FROM c WHERE {where_clause}
            ORDER BY
                CASE c.severity
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END
        """

        items = []
        async for item in container.query_items(query=query, parameters=params):
            items.append(item)

        return items

    async def update_resolution(
        self,
        finding_id: str,
        session_id: str,
        resolution_state: str,
    ) -> dict[str, Any] | None:
        """Update finding resolution state.

        Args:
            finding_id: Finding ID
            session_id: Review session ID (partition key)
            resolution_state: New resolution state ('open' or 'resolved')

        Returns:
            Updated finding or None if not found
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            findings = _memory_store.get(session_id, [])
            for f in findings:
                if f.get("id") == finding_id:
                    f["resolutionState"] = resolution_state
                    f["updatedAt"] = datetime.utcnow().isoformat()
                    return f
            return None

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        existing = await self.get(finding_id, session_id)
        if not existing:
            return None

        existing["resolutionState"] = resolution_state
        existing["updatedAt"] = datetime.utcnow().isoformat()

        result = await container.replace_item(item=finding_id, body=existing)
        return result

    async def count_by_session(self, session_id: str) -> dict[str, int]:
        """Count findings by severity for a session.

        Args:
            session_id: Review session ID

        Returns:
            Dict with severity counts
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            findings = _memory_store.get(session_id, [])
            counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}
            for f in findings:
                severity = f.get("severity", "low")
                if severity in counts:
                    counts[severity] += 1
                counts["total"] += 1
            return counts

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        query = """
            SELECT
                COUNT(c.severity = 'critical' ? 1 : undefined) as critical,
                COUNT(c.severity = 'high' ? 1 : undefined) as high,
                COUNT(c.severity = 'medium' ? 1 : undefined) as medium,
                COUNT(c.severity = 'low' ? 1 : undefined) as low,
                COUNT(1) as total
            FROM c WHERE c.reviewSessionId = @sessionId
        """
        params = [{"name": "@sessionId", "value": session_id}]

        items = []
        async for item in container.query_items(query=query, parameters=params):
            items.append(item)

        return items[0] if items else {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}

    async def get_total_count(self, user_id: str | None = None) -> int:
        """Get total findings count.

        Args:
            user_id: Filter by user (optional, requires cross-partition join)

        Returns:
            Total count of findings
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            return sum(len(findings) for findings in _memory_store.values())

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        query = "SELECT VALUE COUNT(1) FROM c"
        items = []
        async for item in container.query_items(
            query=query, enable_cross_partition_query=True
        ):
            items.append(item)

        return items[0] if items else 0


# Singleton instance
_repository: FindingsRepository | None = None


def get_findings_repository() -> FindingsRepository:
    """Get or create repository instance."""
    global _repository
    if _repository is None:
        _repository = FindingsRepository()
    return _repository
