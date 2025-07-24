from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./demo.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Azure
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GenomeCostTracker"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:4200", "https://genomecost.vercel.app"]
    
    # Cost estimation
    AZURE_BATCH_COST_PER_HOUR: float = 0.096  # Standard_D2s_v3
    AZURE_STORAGE_HOT_COST_PER_GB: float = 0.0184
    AZURE_STORAGE_COOL_COST_PER_GB: float = 0.01
    AZURE_NETWORK_COST_PER_GB: float = 0.087
    
    class Config:
        env_file = ".env"

settings = Settings()