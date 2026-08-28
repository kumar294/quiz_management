from datetime import datetime

from app.schemas.domain import (
    CompanyBrief,
    Difficulty,
    Gap,
    GapReport,
    InterviewQuestion,
    LearningResource,
    PerformanceReport,
    PrepPlan,
    QuestionBank,
    ResourcePlan,
    ResumeBullet,
    RubricScore,
    TailoredResume,
)


def _sample_plan() -> PrepPlan:
    brief = CompanyBrief(
        company="Acme",
        role="APM",
        business_summary="B2B SaaS.",
        interview_process=["R1 — case", "R2 — behavioral"],
        themes=["prioritization"],
        culture_signals=["low ego"],
        citations=["alumni_1"],
    )
    tailored = TailoredResume(
        student_id="s1",
        company="Acme",
        role="APM",
        bullets=[ResumeBullet(section="Experience", rewritten="Shipped X", tags=["SQL"])],
        summary_line="MBA candidate with 3y ops experience targeting APM roles.",
        coverage_score=0.6,
    )
    gaps = GapReport(
        student_id="s1",
        company="Acme",
        role="APM",
        gaps=[Gap(skill="SQL", severity="high", evidence="one project", suggested_focus_hours=8)],
        strengths=["stakeholder mgmt"],
    )
    questions = QuestionBank(
        company="Acme",
        role="APM",
        questions=[
            InterviewQuestion(
                category="behavioral",
                difficulty=Difficulty.medium,
                prompt="Tell me about a tradeoff you made.",
                ideal_answer_outline=["situation", "options", "decision", "result"],
            )
        ],
    )
    resources = ResourcePlan(
        student_id="s1",
        company="Acme",
        ordered_resources=[
            LearningResource(title="Mode SQL", type="course", addresses_skills=["SQL"], est_hours=6)
        ],
        total_hours=6,
    )
    return PrepPlan(
        id="p1",
        student_id="s1",
        company="Acme",
        role="APM",
        brief=brief,
        resume=tailored,
        gaps=gaps,
        questions=questions,
        resources=resources,
        generated_at=datetime.utcnow(),
    )


def test_prep_plan_roundtrip() -> None:
    plan = _sample_plan()
    dumped = plan.model_dump(mode="json")
    restored = PrepPlan.model_validate(dumped)
    assert restored.company == "Acme"
    assert restored.gaps.gaps[0].severity == "high"


def test_performance_report_bounds() -> None:
    report = PerformanceReport(
        student_id="s1",
        session_id="m1",
        scores=[RubricScore(dimension="structure", score=3.5, comment="ok")],
        overall=3.5,
        next_actions=["redo Q3"],
    )
    assert 0 <= report.overall <= 5
