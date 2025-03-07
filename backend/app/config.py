# backend/app/config.py
import os
import sys
from pydantic_settings import BaseSettings
from typing import Optional

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    PINECONE_HOST_SUFFIX: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_DOMAIN: str
    AUTH0_CALLBACK_URL: str
    OPENDR_URL: Optional[str] = None
    REDIS_HOST: Optional[str] = "127.0.0.1"
    REDIS_PORT: Optional[int] = 6379
    REDIS_PASSWORD: Optional[str] = ""
    REDIS_DB: Optional[int] = 0
    OPENAI_API_KEY: Optional[str] = None
    API_SCHEME: Optional[str] = "http"
    API_PORT: Optional[int] = 8000
    API_HOST: Optional[str] = "localhost"
    CLIENT_URL: Optional[str] = "http://localhost:3000"
    MAILTRAP_USERNAME: Optional[str] = "your-mailtrap-username"
    MAILTRAP_PASSWORD: Optional[str] = "your-mailtrap-password"
    MAILTRAP_HOST: Optional[str] = "live.smtp.mailtrap.io"
    MAILTRAP_PORT: Optional[int] = 587
    # JWT Configuration
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    
    class Config:
        env_file = os.path.join(FILE_PATH,"..", ".env")
        env_file_encoding = "utf-8"

settings = Settings()
