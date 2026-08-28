from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents import score_performance
from app.orchestration.graph import generate_prep_plan
from app.schemas.domain import MockSession, PerformanceReport, PrepPlan

router = APIRouter(prefix="/api", tags=["prep"])


class GeneratePlanRequest(BaseModel):
    student_id: str
    student_profile: dict
    resume: str
    company: str
    role: str
    jd: dict
    alumni: list[dict] = []
    public: list[dict] = []


@router.post("/plans", response_model=PrepPlan)
async def create_plan(req: GeneratePlanRequest) -> PrepPlan:
    try:
        return await generate_prep_plan(**req.model_dump())
    except Exception as e:  # noqa: BLE001 — surface upstream failures to the caller
        raise HTTPException(status_code=502, detail=f"pipeline_failed: {e}") from e


class ScoreMockRequest(BaseModel):
    student_id: str
    company: str
    role: str
    transcript: str
    duration_minutes: int
    prior_reports: list[dict] = []


@router.post("/mock-sessions/score", response_model=PerformanceReport)
async def score_mock(req: ScoreMockRequest) -> PerformanceReport:
    session = MockSession(
        id=str(uuid.uuid4()),
        student_id=req.student_id,
        company=req.company,
        role=req.role,
        transcript=req.transcript,
        duration_minutes=req.duration_minutes,
        at=datetime.utcnow(),
    )
    return await score_performance({
        "session": session.model_dump(mode="json"),
        "prior_reports": req.prior_reports,
    })
