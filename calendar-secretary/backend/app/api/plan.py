from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.event import Event, TaskFamily, UserPomodoroSettings
from app.schemas.plan import PlanSolution, ProposalResponse, SolveRequest
from app.services.planner.cp_sat_solver import CPSATSolver
from app.services.planner.heuristic_solver import HeuristicPlanner

router = APIRouter()


def _load_context(db: Session) -> tuple[list[Event], dict[str, TaskFamily], UserPomodoroSettings | None]:
    events = db.query(Event).all()
    families = {family.key: family for family in db.query(TaskFamily).all()}
    pomodoro = db.query(UserPomodoroSettings).first()
    return events, families, pomodoro


@router.post("/solve", response_model=PlanSolution)
async def solve_plan(payload: SolveRequest, db: Session = Depends(get_db)) -> PlanSolution:
    events, families, pomodoro = _load_context(db)
    solver = CPSATSolver()
    try:
        solution = solver.solve(events, families, pomodoro, payload.from_dt, payload.to_dt)
        selected_solver = "cp-sat"
    except Exception as exc:  # pragma: no cover - fallback path
        heuristic = HeuristicPlanner()
        solution = heuristic.solve(events, families, pomodoro, payload.from_dt, payload.to_dt)
        selected_solver = f"heuristic:{exc}"
    if solution is None:
        raise HTTPException(status_code=422, detail="Unable to produce plan")
    solution.solver = selected_solver
    return solution


@router.get("/proposals", response_model=ProposalResponse)
async def get_proposals(db: Session = Depends(get_db)) -> ProposalResponse:
    heuristic = HeuristicPlanner()
    events, families, pomodoro = _load_context(db)
    return heuristic.propose(events, families, pomodoro)
