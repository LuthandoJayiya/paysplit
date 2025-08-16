from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = Field(default="Auth User Service", env='APP_NAME')
    app_version: str = Field(default="1.0.0", env='APP_VERSION')
    debug: bool = Field(default=False, env='DEBUG')
    secret_key: str = Field(default="your-secret-key-here", env='SECRET_KEY')
    firebase_credentials: Path = Field(..., env='FIREBASE_CREDENTIALS')
    firebase_api_key: str
    secret_key: str

    class Config:
        env_file = ".env"
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()
