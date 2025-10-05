import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class EventType(str, Enum):
    fixed = "fixed"
    flexible = "flexible"


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    duration_min = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False, default=5)
    deadline = Column(DateTime(timezone=True), nullable=True)
    time_windows = Column(JSON, nullable=True)
    flex = Column(JSON, nullable=True)
    location = Column(String, nullable=True)
    travel_time_min = Column(Integer, default=0, nullable=False)
    calendar_id = Column(String, nullable=True)
    external_ids = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    family_key = Column(String, nullable=True)
    pomodoro_opt_in = Column(Boolean, default=False, nullable=False)

    dependencies = relationship(
        "TaskDependency",
        back_populates="task",
        cascade="all, delete-orphan",
        foreign_keys="TaskDependency.task_id",
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    depends_on_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(2), nullable=False)
    lag_min = Column(Integer, nullable=False, default=0)

    task = relationship("Event", foreign_keys=[task_id], back_populates="dependencies")
    depends_on = relationship("Event", foreign_keys=[depends_on_id])


class TaskFamily(Base):
    __tablename__ = "task_families"

    key = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    min_daily_minutes = Column(Integer, nullable=True)
    weekly_target_minutes = Column(Integer, nullable=True)
    max_daily_minutes = Column(Integer, nullable=True)


class UserPomodoroSettings(Base):
    __tablename__ = "user_pomodoro_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    enabled = Column(Boolean, nullable=False, default=False)
    pomodoro_len_min = Column(Integer, nullable=False, default=25)
    short_break_min = Column(Integer, nullable=False, default=5)
    long_break_min = Column(Integer, nullable=False, default=15)
    long_break_every = Column(Integer, nullable=False, default=4)
