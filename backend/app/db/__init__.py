# backend/app/db/__init__.py

from app.db.database import AsyncSessionLocal

async def get_db():
    """Dependency that provides an async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()