"""Pydantic schemas — the wire and inter-agent contract.

Keep these narrow: only fields the agents or API actually read/write. ORM models
in `app/models/` may carry additional bookkeeping fields (timestamps, foreign keys).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------- Core entities ----------

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Student(BaseModel):
    id: str
    name: str
    email: str
    program: str = "PGPM"
    cohort_year: int
    profile: dict = Field(default_factory=dict)   # work-ex, skills, interests
    target_companies: list[str] = Field(default_factory=list)
    prep_time_logs: list["PrepTimeLog"] = Field(default_factory=list)
    baseline_confidence: float | None = None      # 1-10 self-report at onboarding
    post_confidence: float | None = None          # 1-10 self-report after prep


class PrepTimeLog(BaseModel):
    company: str
    minutes: int
    source: Literal["manual", "agent"] = "agent"
    at: datetime


class CompanyJD(BaseModel):
    id: str
    company: str
    role: str
    seniority: str | None = None
    description: str
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    source_url: str | None = None


class AlumniExperience(BaseModel):
    id: str
    company: str
    role: str
    year: int
    author: str | None = None                     # anonymized handle
    difficulty: Difficulty
    rounds: list[str] = Field(default_factory=list)
    write_up: str


class PublicInterviewData(BaseModel):
    id: str
    company: str
    role: str | None = None
    source: Literal["glassdoor", "ambitionbox", "prepinsta"]
    questions: list[str] = Field(default_factory=list)
    reviews: list[str] = Field(default_factory=list)
    fetched_at: datetime


# ---------- Agent outputs ----------

class CompanyBrief(BaseModel):
    """Output of the Company Research agent."""
    company: str
    role: str
    business_summary: str
    interview_process: list[str]                  # ordered rounds
    themes: list[str]                             # recurring interview themes
    culture_signals: list[str]
    citations: list[str] = Field(default_factory=list)  # source ids / URLs


class ResumeBullet(BaseModel):
    section: str                                  # "Experience" / "Projects" / ...
    original: str | None = None
    rewritten: str
    tags: list[str] = Field(default_factory=list) # which JD skills it targets


class TailoredResume(BaseModel):
    student_id: str
    company: str
    role: str
    bullets: list[ResumeBullet]
    summary_line: str
    coverage_score: float                         # 0-1, how much of JD is covered


class Gap(BaseModel):
    skill: str
    severity: Literal["low", "medium", "high"]
    evidence: str                                 # why we think it's a gap
    suggested_focus_hours: int


class GapReport(BaseModel):
    student_id: str
    company: str
    role: str
    gaps: list[Gap]
    strengths: list[str]


class InterviewQuestion(BaseModel):
    category: Literal["behavioral", "technical", "case", "guesstimate", "hr"]
    difficulty: Difficulty
    prompt: str
    ideal_answer_outline: list[str]
    tags: list[str] = Field(default_factory=list)


class QuestionBank(BaseModel):
    company: str
    role: str
    questions: list[InterviewQuestion]


class LearningResource(BaseModel):
    title: str
    url: str | None = None
    type: Literal["course", "article", "book", "video", "practice"]
    addresses_skills: list[str]
    est_hours: float


class ResourcePlan(BaseModel):
    student_id: str
    company: str
    ordered_resources: list[LearningResource]     # study in this order
    total_hours: float


class MockSession(BaseModel):
    id: str
    student_id: str
    company: str
    role: str
    transcript: str
    duration_minutes: int
    at: datetime
    self_confidence: float | None = None          # 1-10 after this session


class RubricScore(BaseModel):
    dimension: Literal["structure", "content", "communication", "domain", "confidence"]
    score: float                                  # 0-5
    comment: str


class PerformanceReport(BaseModel):
    student_id: str
    session_id: str
    scores: list[RubricScore]
    overall: float
    longitudinal_delta: float | None = None       # vs. prior session, if any
    next_actions: list[str]


class PrepPlan(BaseModel):
    """Everything one student needs for one company. Persisted per (student, company)."""
    id: str
    student_id: str
    company: str
    role: str
    brief: CompanyBrief
    resume: TailoredResume
    gaps: GapReport
    questions: QuestionBank
    resources: ResourcePlan
    generated_at: datetime
    student_ready_at: datetime | None = None      # user marks when they feel ready
    performance: list[PerformanceReport] = Field(default_factory=list)
