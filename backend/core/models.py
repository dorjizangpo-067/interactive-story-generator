from typing import Any

from pydantic import BaseModel, Field


class StoryOptionLLM(BaseModel):
    text: str = Field(description="Text of the option user shown to the user")
    nextNode: dict[str, Any] = Field(
        description="The next node content and it's options"
    )


class StoryNodeLLM(BaseModel):
    content: str = Field(description="The main content of the story node")
    isEnding: bool = Field(description="Wheather this node is an ending node")
    isWinningEnding: bool = Field(
        description="Wheather this node is winning ending node"
    )
    options: list[StoryOptionLLM] | None = Field(
        default=None, description="The options for this node"
    )


class StoryLLMResponse(BaseModel):
    title: str = Field(description="The title of the story")
    rootNode: StoryNodeLLM = Field(description="The rood node of the story")
