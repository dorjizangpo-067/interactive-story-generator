from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StoryOptionsSchemas(BaseModel):
    text: str
    node_id: int | None = None


class StoryNodeBase(BaseModel):
    content: str
    is_ending: bool = False
    is_winning_ending: bool = False


class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: list[StoryOptionsSchemas] = []

    model_config = ConfigDict(from_attributes=True)


class StoryBase(BaseModel):
    title: str
    session_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CreateStoryRequest(BaseModel):
    theme: str
    model_config = ConfigDict(from_attributes=True)


class CompleteStoryResponse(StoryBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: dict[int, CompleteStoryNodeResponse]
