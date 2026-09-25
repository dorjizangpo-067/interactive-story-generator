import uuid
from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import SessionLocal, get_db
from models.job import StoryJob
from models.story import Story, StoryNode
from schemas.job import StoryJobResponse
from schemas.story import (
    CompleteStoryResponse,
    CreateStoryRequest,
)

router = APIRouter(
    prefix="/stories",
    tags=["Story"],
)


def get_session_id(session_id: Annotated[str | None, Cookie()] = None):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/create")
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: Annotated[str, Depends(get_session_id)],
    db: Annotated[Session, Depends(get_db)],
) -> StoryJobResponse:
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="Pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        generate_story_task, job_id=job_id, theme=request.theme, session_id=session_id
    )

    return StoryJobResponse.model_validate(job)


def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()

    try:
        job = db.execute(
            select(StoryJob).where(StoryJob.job_id == job_id)
        ).scalar_one_or_none()

        if not job:
            return

        try:
            job.status = "Processing"
            db.commit()
            db.refresh(job)

            story = {}  # TODO: generate Story

            job.story_id = 1  # TODO: update story id
            job.status = "Completed"
            job.created_at = datetime.now()
            db.commit()
            db.refresh(job)

        except Exception as e:
            db.rollback()
            job.status = "Failed"
            job.created_at = datetime.now()
            job.error = str(e)
            db.commit()
            db.refresh(job)
    finally:
        db.close()


@router.get("/{story_id}/complete")
def complete_story(
    story_id: int, db: Annotated[Session, Depends(get_db)]
) -> CompleteStoryResponse:

    story = db.execute(select(Story).where(Story.id == story_id)).scalar_one_or_none()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story Not Found"
        )
    # TODO: parse story
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=next(n for n in story.nodes if n.is_root),
        all_nodes={n.id: n for n in story.nodes},
    )
