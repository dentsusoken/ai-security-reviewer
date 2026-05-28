"""
Review Session Repository.

Handles persistence of review sessions to Cosmos DB.
Falls back to in-memory storage when Cosmos DB is not configured.
"""

import logging
from datetime import datetime
from typing import Any

from app.services.cosmos_service import get_cosmos_service

logger = logging.getLogger(__name__)

# In-memory storage fallback
_memory_store: dict[str, dict[str, Any]] = {}


class ReviewSessionRepository:
    """Repository for review session persistence."""

    CONTAINER_NAME = "reviewSessions"

    def __init__(self) -> None:
        """Initialize repository."""
        self._cosmos_service = None

    async def _ensure_cosmos(self) -> None:
        """Ensure Cosmos DB service is initialized."""
        if self._cosmos_service is None:
            self._cosmos_service = await get_cosmos_service()

    async def create(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new review session.

        Args:
            session_data: Session data including id, userId, etc.

        Returns:
            Created session data with Cosmos metadata
        """
        await self._ensure_cosmos()

        # Add timestamps if not present
        if "createdAt" not in session_data:
            session_data["createdAt"] = datetime.utcnow().isoformat()

        if self._cosmos_service.is_mock_mode:
            # In-memory storage
            session_id = session_data["id"]
            _memory_store[session_id] = session_data.copy()
            logger.debug(f"Stored session {session_id} in memory")
            return session_data

        # Cosmos DB storage
        container = self._cosmos_service.get_container(self.CONTAINER_NAME)
        result = await container.create_item(body=session_data)
        logger.debug(f"Created session {session_data['id']} in Cosmos DB")
        return result

    async def get(self, session_id: str, user_id: str) -> dict[str, Any] | None:
        """Get a review session by ID.

        Args:
            session_id: Session ID
            user_id: User ID (partition key)

        Returns:
            Session data or None if not found
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            return _memory_store.get(session_id)

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)
        try:
            result = await container.read_item(item=session_id, partition_key=user_id)
            return result
        except Exception:
            return None

    async def get_by_id(self, session_id: str) -> dict[str, Any] | None:
        """Get a review session by ID (without partition key).

        Note: This performs a cross-partition query - use get() when user_id is known.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            return _memory_store.get(session_id)

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": session_id}]

        items = []
        async for item in container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ):
            items.append(item)

        return items[0] if items else None

    async def update(
        self, session_id: str, user_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update a review session.

        Args:
            session_id: Session ID
            user_id: User ID (partition key)
            updates: Fields to update

        Returns:
            Updated session data or None if not found
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            if session_id not in _memory_store:
                return None
            _memory_store[session_id].update(updates)
            _memory_store[session_id]["updatedAt"] = datetime.utcnow().isoformat()
            return _memory_store[session_id]

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        # Read current document
        existing = await self.get(session_id, user_id)
        if not existing:
            return None

        # Merge updates
        existing.update(updates)
        existing["updatedAt"] = datetime.utcnow().isoformat()

        # Replace document
        result = await container.replace_item(item=session_id, body=existing)
        return result

    async def list_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
        input_type: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """List review sessions for a user.

        Args:
            user_id: User ID (partition key)
            limit: Maximum number of results
            offset: Number of results to skip
            status: Filter by status (optional)
            input_type: Filter by input type (optional)

        Returns:
            Tuple of (sessions list, total count)
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            # Filter in-memory store
            sessions = [
                s
                for s in _memory_store.values()
                if s.get("userId") == user_id
                and (status is None or s.get("status") == status)
                and (input_type is None or s.get("inputType") == input_type)
            ]
            # Sort by startedAt descending
            sessions.sort(key=lambda x: x.get("startedAt", ""), reverse=True)
            total = len(sessions)
            return sessions[offset : offset + limit], total

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        # Build query
        conditions = ["c.userId = @userId"]
        params = [{"name": "@userId", "value": user_id}]

        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})

        if input_type:
            conditions.append("c.inputType = @inputType")
            params.append({"name": "@inputType", "value": input_type})

        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
        count_items = []
        async for item in container.query_items(query=count_query, parameters=params):
            count_items.append(item)
        total = count_items[0] if count_items else 0

        # Data query
        query = f"""
            SELECT * FROM c WHERE {where_clause}
            ORDER BY c.startedAt DESC
            OFFSET @offset LIMIT @limit
        """
        params.extend(
            [
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit},
            ]
        )

        items = []
        async for item in container.query_items(query=query, parameters=params):
            items.append(item)

        return items, total

    async def list_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """List all review sessions (cross-partition).

        Note: Use sparingly - cross-partition queries are expensive.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            status: Filter by status (optional)

        Returns:
            Tuple of (sessions list, total count)
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            sessions = list(_memory_store.values())
            if status:
                sessions = [s for s in sessions if s.get("status") == status]
            sessions.sort(key=lambda x: x.get("startedAt", ""), reverse=True)
            total = len(sessions)
            return sessions[offset : offset + limit], total

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        conditions = []
        params = []

        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Count query
        count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
        count_items = []
        async for item in container.query_items(
            query=count_query,
            parameters=params,
            enable_cross_partition_query=True,
        ):
            count_items.append(item)
        total = count_items[0] if count_items else 0

        # Data query
        query = f"""
            SELECT * FROM c WHERE {where_clause}
            ORDER BY c.startedAt DESC
            OFFSET @offset LIMIT @limit
        """
        params.extend(
            [
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit},
            ]
        )

        items = []
        async for item in container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True,
        ):
            items.append(item)

        return items, total

    async def get_stats(self, user_id: str | None = None) -> dict[str, Any]:
        """Get review statistics.

        Args:
            user_id: User ID to filter by (optional, None for all users)

        Returns:
            Statistics including counts and averages
        """
        await self._ensure_cosmos()

        if self._cosmos_service.is_mock_mode:
            sessions = list(_memory_store.values())
            if user_id:
                sessions = [s for s in sessions if s.get("userId") == user_id]

            total = len(sessions)
            completed = len([s for s in sessions if s.get("status") == "completed"])
            scores = [
                s.get("scoreSummary", {}).get("overall", 0)
                for s in sessions
                if s.get("status") == "completed"
            ]
            avg_score = sum(scores) / len(scores) if scores else 0

            return {
                "totalReviews": total,
                "completedReviews": completed,
                "averageScore": round(avg_score),
            }

        container = self._cosmos_service.get_container(self.CONTAINER_NAME)

        if user_id:
            query = """
                SELECT
                    COUNT(1) as totalReviews,
                    COUNT(c.status = 'completed' ? 1 : undefined) as completedReviews
                FROM c WHERE c.userId = @userId
            """
            params = [{"name": "@userId", "value": user_id}]
        else:
            query = """
                SELECT
                    COUNT(1) as totalReviews,
                    COUNT(c.status = 'completed' ? 1 : undefined) as completedReviews
                FROM c
            """
            params = []

        items = []
        async for item in container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True,
        ):
            items.append(item)

        stats = items[0] if items else {"totalReviews": 0, "completedReviews": 0}
        stats["averageScore"] = 0  # TODO: Calculate from completed reviews

        return stats


# Singleton instance
_repository: ReviewSessionRepository | None = None


def get_review_session_repository() -> ReviewSessionRepository:
    """Get or create repository instance."""
    global _repository
    if _repository is None:
        _repository = ReviewSessionRepository()
    return _repository
