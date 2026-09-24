from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StoryJobBase(BaseModel):
    theme: str


class StoryJobResponse(BaseModel):
    job_id: int
    status: str
    create_at: datetime
    story_id: int | None = None
    completed_at: datetime | None = None
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class StoryJobCreate(StoryJobBase):
    pass
