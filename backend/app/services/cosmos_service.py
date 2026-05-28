"""
Cosmos DB Client Service.

Provides a connection to Azure Cosmos DB using DefaultAzureCredential (Managed Identity).
Falls back to in-memory storage when Cosmos DB is not configured.
"""

import logging
from typing import Any

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from app.core.config import settings

logger = logging.getLogger(__name__)


class CosmosDBService:
    """Azure Cosmos DB connection service."""

    _instance: "CosmosDBService | None" = None
    _client: CosmosClient | None = None
    _database: Any = None
    _containers: dict[str, Any] = {}
    _mock_mode: bool = False

    def __new__(cls) -> "CosmosDBService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> None:
        """Initialize Cosmos DB connection."""
        if not settings.cosmos_enabled:
            logger.warning(
                "Cosmos DB not configured - using in-memory storage. "
                "Set AZURE_COSMOS_ENDPOINT to enable persistence."
            )
            self._mock_mode = True
            return

        try:
            credential = DefaultAzureCredential()
            self._client = CosmosClient(
                url=settings.azure_cosmos_endpoint,
                credential=credential,
            )
            self._database = self._client.get_database_client(
                settings.azure_cosmos_database
            )
            logger.info(
                f"Connected to Cosmos DB: {settings.azure_cosmos_database}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Cosmos DB: {e}")
            logger.warning("Falling back to in-memory storage")
            self._mock_mode = True

    async def close(self) -> None:
        """Close Cosmos DB connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._database = None
            self._containers.clear()

    @property
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode (in-memory)."""
        return self._mock_mode

    def get_container(self, container_name: str) -> Any:
        """Get a container client.

        Args:
            container_name: Name of the container

        Returns:
            Container client or None if in mock mode
        """
        if self._mock_mode:
            return None

        if container_name not in self._containers:
            self._containers[container_name] = self._database.get_container_client(
                container_name
            )
        return self._containers[container_name]


# Global instance
_cosmos_service: CosmosDBService | None = None


async def get_cosmos_service() -> CosmosDBService:
    """Get or create Cosmos DB service instance."""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosDBService()
        await _cosmos_service.initialize()
    return _cosmos_service


async def close_cosmos_service() -> None:
    """Close Cosmos DB service."""
    global _cosmos_service
    if _cosmos_service:
        await _cosmos_service.close()
        _cosmos_service = None
