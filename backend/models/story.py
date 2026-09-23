from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    session_id: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    nodes: Mapped[list["StoryNode"]] = relationship(back_populates="story")


class StoryNode(Base):
    __tablename__ = "story_nodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str]
    is_root: Mapped[bool] = mapped_column(default=False)
    is_ending: Mapped[bool] = mapped_column(default=False)
    is_winning_ending: Mapped[bool] = mapped_column(default=False)
    options: Mapped[list] = mapped_column(JSON, default=list)

    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), index=True)
    story: Mapped["Story"] = relationship(back_populates="nodes")
