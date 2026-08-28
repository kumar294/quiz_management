"""SQLAlchemy ORM. Kept minimal — full-text/JSON columns for anything the agents own,
typed columns for anything the app queries."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class StudentRow(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    baseline_confidence: Mapped[float | None] = mapped_column(default=None)
    post_confidence: Mapped[float | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    plans: Mapped[list[PrepPlanRow]] = relationship(back_populates="student")


class CompanyJDRow(Base):
    __tablename__ = "company_jds"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    company: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON)


class AlumniExperienceRow(Base):
    __tablename__ = "alumni_experiences"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    company: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column()
    data: Mapped[dict] = mapped_column(JSON)


class PublicInterviewDataRow(Base):
    __tablename__ = "public_interview_data"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    company: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(DateTime)


class PrepPlanRow(Base):
    __tablename__ = "prep_plans"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    company: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)
    plan: Mapped[dict] = mapped_column(JSON)      # the full PrepPlan schema
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student_ready_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    student: Mapped[StudentRow] = relationship(back_populates="plans")


class MockSessionRow(Base):
    __tablename__ = "mock_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    company: Mapped[str] = mapped_column(String, index=True)
    transcript: Mapped[str] = mapped_column(String)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    report: Mapped[dict | None] = mapped_column(JSON, default=None)


def init_db() -> None:
    Base.metadata.create_all(engine)
