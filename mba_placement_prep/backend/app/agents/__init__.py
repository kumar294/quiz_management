from app.agents.base import run_agent
from app.schemas.domain import (
    CompanyBrief,
    GapReport,
    PerformanceReport,
    QuestionBank,
    ResourcePlan,
    TailoredResume,
)


async def research_company(payload: dict) -> CompanyBrief:
    return await run_agent(prompt_name="company_research", payload=payload, schema=CompanyBrief)


async def tailor_resume(payload: dict) -> TailoredResume:
    return await run_agent(prompt_name="resume_tailoring", payload=payload, schema=TailoredResume)


async def analyze_gaps(payload: dict) -> GapReport:
    return await run_agent(prompt_name="gap_analysis", payload=payload, schema=GapReport)


async def generate_questions(payload: dict) -> QuestionBank:
    return await run_agent(prompt_name="interview_questions", payload=payload, schema=QuestionBank)


async def recommend_resources(payload: dict) -> ResourcePlan:
    return await run_agent(prompt_name="learning_resources", payload=payload, schema=ResourcePlan)


async def score_performance(payload: dict) -> PerformanceReport:
    return await run_agent(
        prompt_name="performance_tracking", payload=payload, schema=PerformanceReport
    )
