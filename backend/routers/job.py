from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import get_db
from models.job import StoryJob
from schemas.job import StoryJobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/job_id")
def get_job_status(
    job_id: str, db: Annotated[Session, Depends(get_db)]
) -> StoryJobResponse:
    job = db.execute(
        select(StoryJob).where(StoryJob.job_id == job_id)
    ).scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job Not Found"
        )
    return StoryJobResponse.model_validate(job)
