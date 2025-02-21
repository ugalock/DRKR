from fastapi import FastAPI

from app.routers.auth import router as AuthRouter
from app.routers.comments import router as CommentsRouter
from app.routers.deep_research import router as DeepResearchRouter
from app.routers.organizations import router as OrganizationsRouter
from app.routers.ratings import router as RatingsRouter
from app.routers.research_jobs import router as ResearchJobsRouter
from app.routers.search import router as SearchRouter
from app.routers.tags import router as TagsRouter
from app.routers.users import router as UsersRouter

app = FastAPI(
    title="DRKR API",
    description="A sample OpenAPI specification for the DRKR project, covering all endpoint stubs across authentication, users, organizations, deep research items, tags, comments, ratings, research jobs, and search. ",
    version="1.0.0",
)

app.include_router(AuthRouter)
app.include_router(CommentsRouter)
app.include_router(DeepResearchRouter)
app.include_router(OrganizationsRouter)
app.include_router(RatingsRouter)
app.include_router(ResearchJobsRouter)
app.include_router(SearchRouter)
app.include_router(TagsRouter)
app.include_router(UsersRouter)
