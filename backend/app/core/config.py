import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    """Application settings."""

    app_name: str = os.getenv("APP_NAME", "AI Security Reviewer API")

    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://lively-rock-0490c3d00.7.azurestaticapps.net",  # Azure SWA
    ]

    # API settings
    api_prefix: str = ""

    # Azure Entra ID settings
    azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")
    azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")

    # Authentication settings
    auth_disabled: bool = os.getenv("AUTH_DISABLED", "false").lower() == "true"


settings = Settings()
