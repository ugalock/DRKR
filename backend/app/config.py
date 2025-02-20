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
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    API_PORT: Optional[int] = 8000
    # Add any other env variables you need here...
    
    class Config:
        env_file = os.path.join(FILE_PATH,"..", ".env")
        env_file_encoding = "utf-8"

settings = Settings()
