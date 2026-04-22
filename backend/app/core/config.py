from pydantic_settings import BaseSettings
from typing import List, Literal
import os


class Settings(BaseSettings):
    # Server Configuration
    NODE_ENV: str = "development"
    PORT: int = 8000
    LOG_LEVEL: str = "info"
    DEBUG: bool = True
    
    # Database Configuration
    MONGODB_URI: str
    MONGODB_DATABASE: str = "bloodbank"
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Provider Configuration
    AI_PROVIDER: Literal["openai", "gemini"] = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    S3_BASE_URL: str = ""
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    
    # OneSignal Configuration
    ONESIGNAL_APP_ID: str = ""
    ONESIGNAL_API_KEY: str = ""
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "*"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Email Configuration (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    
    # Redis Configuration (optional)
    REDIS_URL: str = ""
    
    # Security
    SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validate AI provider configuration
        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        elif self.AI_PROVIDER == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")


# Create settings instance
settings = Settings()
