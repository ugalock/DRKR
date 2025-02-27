# backend/app/main.py
import uvicorn
from app.routers import app
from app.config import settings



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True  # Enable auto-reload during development
    )