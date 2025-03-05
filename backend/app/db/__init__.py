# backend/app/db/__init__.py

from contextlib import contextmanager

from app.db.database import AsyncSessionLocal, SessionLocal

async def get_db():
    """Dependency that provides an async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@contextmanager
def get_db_sync():
    """Dependency that provides a sync database session"""
    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.close()