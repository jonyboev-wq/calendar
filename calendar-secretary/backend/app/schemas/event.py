from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TimeWindow(BaseModel):
    start: datetime
    end: datetime


class FlexOptions(BaseModel):
    shift_earliest: datetime | None = None
    shift_latest: datetime | None = None
    max_earlier_minutes: int | None = None
    max_later_minutes: int | None = None
    can_split: bool = False
    min_chunk_min: int | None = None
    max_splits: int | None = None


class ConstraintOptions(BaseModel):
    do_not_disturb: bool = False
    must_daylight: bool = False
    min_buffer_before_min: int = 0
    min_buffer_after_min: int = 0


class MetadataOptions(BaseModel):
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class DependencyRef(BaseModel):
    task_id: UUID
    type: Literal["FS", "SS", "FF", "SF"] = "FS"
    lag_min: int = 0


class EventBase(BaseModel):
    title: str
    type: Literal["fixed", "flexible"]
    duration_min: int
    priority: int = 5
    deadline: datetime | None = None
    time_windows: list[TimeWindow] = Field(default_factory=list)
    flex: FlexOptions | None = None
    location: str | None = None
    travel_time_min: int = 0
    calendar_id: str | None = None
    external_ids: dict[str, str | None] | None = None
    constraints: ConstraintOptions | None = None
    metadata: MetadataOptions | None = None
    family_key: str | None = None
    pomodoro_opt_in: bool = False
    depends_on: list[DependencyRef] = Field(default_factory=list)

    @validator("priority")
    def validate_priority(cls, value: int) -> int:  # noqa: D401
        """Ensure the priority is within the allowed range."""
        if not 1 <= value <= 10:
            raise ValueError("priority must be between 1 and 10")
        return value


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    title: str | None = None
    type: Literal["fixed", "flexible"] | None = None
    duration_min: int | None = None


class EventSchema(EventBase):
    id: UUID

    class Config:
        orm_mode = True
