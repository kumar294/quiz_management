"""LangGraph orchestration for the prep-plan pipeline.

Graph:
    research ──► resume ─┐
              └► gaps ───┼──► questions ──► resources ──► assemble
                         │
                         └── (gaps feeds questions and resources)

Resume and gaps run in parallel after research; questions and resources both wait
on gaps; the terminal `assemble` node writes the full PrepPlan.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents import (
    analyze_gaps,
    generate_questions,
    recommend_resources,
    research_company,
    tailor_resume,
)
from app.schemas.domain import (
    CompanyBrief,
    GapReport,
    PrepPlan,
    QuestionBank,
    ResourcePlan,
    TailoredResume,
)


class PipelineState(TypedDict, total=False):
    # inputs
    student_id: str
    student_profile: dict
    resume: str
    company: str
    role: str
    jd: dict
    alumni: list[dict]
    public: list[dict]
    # outputs
    brief: CompanyBrief
    tailored: TailoredResume
    gaps: GapReport
    questions: QuestionBank
    resources: ResourcePlan
    plan: PrepPlan


async def _research(state: PipelineState) -> dict[str, Any]:
    brief = await research_company({
        "company": state["company"],
        "role": state["role"],
        "jd": state["jd"],
        "alumni": state.get("alumni", []),
        "public": state.get("public", []),
    })
    return {"brief": brief}


async def _resume_and_gaps(state: PipelineState) -> dict[str, Any]:
    tailored_t = tailor_resume({
        "student_id": state["student_id"],
        "resume": state["resume"],
        "brief": state["brief"].model_dump(),
        "jd": state["jd"],
    })
    gaps_t = analyze_gaps({
        "student_id": state["student_id"],
        "resume": state["resume"],
        "brief": state["brief"].model_dump(),
    })
    tailored, gaps = await asyncio.gather(tailored_t, gaps_t)
    return {"tailored": tailored, "gaps": gaps}


async def _questions_and_resources(state: PipelineState) -> dict[str, Any]:
    q_t = generate_questions({
        "brief": state["brief"].model_dump(),
        "gaps": state["gaps"].model_dump(),
    })
    r_t = recommend_resources({
        "student_id": state["student_id"],
        "gaps": state["gaps"].model_dump(),
    })
    questions, resources = await asyncio.gather(q_t, r_t)
    return {"questions": questions, "resources": resources}


def _assemble(state: PipelineState) -> dict[str, Any]:
    plan = PrepPlan(
        id=str(uuid.uuid4()),
        student_id=state["student_id"],
        company=state["company"],
        role=state["role"],
        brief=state["brief"],
        resume=state["tailored"],
        gaps=state["gaps"],
        questions=state["questions"],
        resources=state["resources"],
        generated_at=datetime.utcnow(),
    )
    return {"plan": plan}


def build_graph():
    g: StateGraph = StateGraph(PipelineState)
    g.add_node("research", _research)
    g.add_node("resume_and_gaps", _resume_and_gaps)
    g.add_node("questions_and_resources", _questions_and_resources)
    g.add_node("assemble", _assemble)

    g.set_entry_point("research")
    g.add_edge("research", "resume_and_gaps")
    g.add_edge("resume_and_gaps", "questions_and_resources")
    g.add_edge("questions_and_resources", "assemble")
    g.add_edge("assemble", END)
    return g.compile()


_graph = None


async def generate_prep_plan(**inputs: Any) -> PrepPlan:
    global _graph
    if _graph is None:
        _graph = build_graph()
    result = await _graph.ainvoke(inputs)
    return result["plan"]
