from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import create_tables
from routers import job, story

create_tables()

app = FastAPI(
    title="Choose Your Own Adventure Game API",
    description="API to generate cool story",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)
