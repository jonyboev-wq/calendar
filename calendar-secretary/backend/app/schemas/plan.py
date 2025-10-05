from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduledChunk(BaseModel):
    event_id: UUID
    chunk_id: str
    start: datetime
    end: datetime
    is_break: bool = False
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadata")

    class Config:
        allow_population_by_field_name = True


class PlanSolution(BaseModel):
    horizon_start: datetime
    horizon_end: datetime
    scheduled: list[ScheduledChunk]
    objective_value: float | None = None
    solver: str


class SolveRequest(BaseModel):
    from_dt: datetime
    to_dt: datetime
    include_proposals: bool = True


class Proposal(BaseModel):
    event_id: UUID
    suggested_start: datetime
    suggested_end: datetime
    score: float
    reasoning: str


class ProposalResponse(BaseModel):
    proposals: list[Proposal]
