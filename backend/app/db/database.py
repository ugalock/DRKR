# backend/app/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Ensure the DATABASE_URL uses the asyncpg driver
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

# Create async engine instead of sync engine
async_engine = create_async_engine(DATABASE_URL, echo=False)
engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://', 1), echo=False)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, expire_on_commit=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
