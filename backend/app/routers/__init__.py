from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.auth import router as AuthRouter
from app.routers.comments import router as CommentsRouter
from app.routers.deep_research import router as DeepResearchRouter
from app.routers.organizations import router as OrganizationsRouter
from app.routers.ratings import router as RatingsRouter
from app.routers.research_jobs import router as ResearchJobsRouter
from app.routers.research_services import router as ResearchServicesRouter
from app.routers.search import router as SearchRouter
from app.routers.tags import router as TagsRouter
from app.routers.users import router as UsersRouter
from app.routers.api_keys import router as ApiKeysRouter

app = FastAPI(
    title="DRKR API",
    description="A sample OpenAPI specification for the DRKR project, covering all endpoint stubs across authentication, users, organizations, deep research items, tags, comments, ratings, research jobs, and search. ",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter, prefix="/api")
app.include_router(CommentsRouter, prefix="/api")
app.include_router(DeepResearchRouter, prefix="/api")
app.include_router(OrganizationsRouter, prefix="/api")
app.include_router(RatingsRouter, prefix="/api")
app.include_router(ResearchJobsRouter, prefix="/api")
app.include_router(ResearchServicesRouter, prefix="/api")
app.include_router(SearchRouter, prefix="/api")
app.include_router(TagsRouter, prefix="/api")
app.include_router(UsersRouter, prefix="/api")
app.include_router(ApiKeysRouter, prefix="/api")
