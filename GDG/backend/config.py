"""
Configuration Management for Ulavan Tholan
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Weather API
    openweather_api_key: Optional[str] = None
    openweather_api_url: str = "https://api.openweathermap.org/data/2.5"
    weatherapi_key: Optional[str] = None
    weatherapi_url: str = "https://api.weatherapi.com/v1"
    
    # Database
    database_url: Optional[str] = None
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # File Upload
    upload_dir: str = "backend/uploads"
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: str = "jpg,jpeg,png"
    
    # ML Model
    model_path: str = "backend/ml/models/plant_disease_model.h5"
    classes_path: str = "backend/ml/models/class_names.json"
    model_confidence_threshold: float = 0.5
    
    # Email (Optional)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@ulavantholan.com"
    
    # SMS (Optional)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    cors_allow_credentials: bool = True
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_size: int = 10485760
    log_backup_count: int = 10
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # External Services
    sentry_dsn: Optional[str] = None
    ga_tracking_id: Optional[str] = None
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


# Helper functions
def is_production() -> bool:
    """Check if running in production"""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development"""
    return settings.environment.lower() == "development"


def get_allowed_origins() -> list:
    """Get list of allowed CORS origins"""
    return [origin.strip() for origin in settings.allowed_origins.split(",")]


def get_allowed_extensions() -> list:
    """Get list of allowed file extensions"""
    return [ext.strip() for ext in settings.allowed_extensions.split(",")]


# Validate critical settings on import
if is_production():
    if settings.secret_key == "dev-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be changed in production!")
    
    if settings.debug:
        print("⚠️  WARNING: Debug mode is enabled in production!")


# Print configuration status
print("\n" + "=" * 60)
print("🌱 Ulavan Tholan - Configuration Loaded")
print("=" * 60)
print(f"Environment: {settings.environment}")
print(f"Debug Mode: {settings.debug}")
print(f"API Host: {settings.api_host}:{settings.api_port}")
print(f"Weather API: {'✅ Configured' if settings.openweather_api_key else '❌ Not configured (using mock data)'}")
print(f"Database: {'✅ Configured' if settings.database_url else '❌ Not configured (using mock data)'}")
print(f"Redis: {'✅ Enabled' if settings.redis_url else '❌ Disabled'}")
print(f"Email: {'✅ Configured' if settings.smtp_user else '❌ Not configured'}")
print(f"SMS: {'✅ Configured' if settings.twilio_account_sid else '❌ Not configured'}")
print("=" * 60 + "\n")
