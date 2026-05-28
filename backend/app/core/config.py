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


settings = Settings()
