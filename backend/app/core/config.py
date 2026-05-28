import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def get_env_list(key: str, default: list[str] | None = None) -> list[str]:
    """Parse comma-separated environment variable into list."""
    value = os.getenv(key)
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    """Application settings."""

    # Application info
    app_name: str = os.getenv("APP_NAME", "AI Security Reviewer API")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS settings
    cors_origins: list[str] = Field(
        default_factory=lambda: get_env_list(
            "CORS_ORIGINS",
            [
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
                "https://lively-rock-0490c3d00.7.azurestaticapps.net",
            ],
        )
    )

    # API settings
    api_prefix: str = os.getenv("API_PREFIX", "")

    # Azure Entra ID settings
    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")

    # Authentication settings
    auth_disabled: bool = os.getenv("AUTH_DISABLED", "false").lower() == "true"

    # Azure OpenAI settings
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )

    # GitHub settings
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_max_files: int = int(os.getenv("GITHUB_MAX_FILES", "20"))
    github_max_file_size: int = int(os.getenv("GITHUB_MAX_FILE_SIZE", "51200"))

    # Review settings
    review_max_code_lines: int = int(os.getenv("REVIEW_MAX_CODE_LINES", "10000"))

    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ("production", "prod")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() in ("development", "dev", "local")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Default settings instance
settings = get_settings()
