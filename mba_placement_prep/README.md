# GLIM Placement Prep — Multi-Agent AI System

An agentic platform that turns scattered placement inputs (JDs, alumni write-ups,
Glassdoor/AmbitionBox/PrepInsta scrapes, student resumes) into a personalized,
company-specific preparation plan for Great Lakes Institute of Management (GLIM)
MBA students.

## Research questions

- **RQ1 — Time savings.** Does agent-generated preparation reduce total prep time
  per target company versus manual synthesis? Measured via `Student.prep_time_logs`
  and per-company `PrepPlan.generated_at → student_ready_at` deltas.
- **RQ2 — Confidence & performance.** Does agent-guided prep improve mock-interview
  scores and self-reported confidence? Measured via `MockSession.scores`,
  longitudinal deltas, and paired baseline vs. post `confidence_score` on `Student`.

## Architecture

```
                    ┌────────────────────────────┐
                    │  Next.js Frontend (App UI) │
                    └──────────────┬─────────────┘
                                   │ REST / SSE
                    ┌──────────────▼─────────────┐
                    │      FastAPI Backend       │
                    │  (auth, storage, routing)  │
                    └──────────────┬─────────────┘
                                   │
                    ┌──────────────▼─────────────┐
                    │  Orchestrator (LangGraph)  │
                    │  Claude Agent SDK pipeline │
                    └──┬──────┬──────┬──────┬────┘
                       │      │      │      │
              ┌────────▼┐ ┌───▼──┐ ┌─▼───┐ ┌▼──────────┐
              │Research │ │Resume│ │ Gap │ │ Questions │
              └────┬────┘ └──┬───┘ └──┬──┘ └─────┬─────┘
                   │         │        │          │
                   └─────────┴────┬───┴──────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │  Resources  ·  Tracking  │
                    └──────────────────────────┘
```

Six specialized agents run as a directed graph, each with a typed input/output
schema, a system prompt in `backend/app/prompts/`, and a thin adapter in
`backend/app/agents/`. The orchestrator persists a `PrepPlan` per (student, company).

## Agents

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | Company Research | company name, role, JD, scraped/alumni text | `CompanyBrief` |
| 2 | Resume Tailoring | student resume + `CompanyBrief` | `TailoredResume` |
| 3 | Gap Analysis | resume + `CompanyBrief` | `GapReport` |
| 4 | Interview Questions | `CompanyBrief` + `GapReport` | `QuestionBank` |
| 5 | Learning Resources | `GapReport` | `ResourcePlan` |
| 6 | Performance Tracking | `MockSession` transcript + history | `PerformanceReport` |

## Data sources

- **First-party**: alumni interview write-ups (Drive exports in `data/alumni/`),
  student resumes uploaded through the app.
- **JDs**: pasted or uploaded through the app; stored in `CompanyJD`.
- **Public**: Glassdoor, AmbitionBox, PrepInsta — ingested via `services/scrapers/`
  under each site's terms; cached in `PublicInterviewData`.

## Setup

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # add ANTHROPIC_API_KEY
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Development

- `pytest` for backend tests, `ruff` for lint, `mypy` for types.
- `npm run lint` / `npm run test` for frontend.
- CI runs both on every push (`.github/workflows/ci.yml`).

## Deployment

Containerize backend (`Dockerfile` in `backend/`), deploy behind any ASGI host
(Fly.io, Render, ECS). Frontend deploys to Vercel. Postgres for `PrepPlan`,
`MockSession`, and longitudinal metrics; S3-compatible bucket for resume/JD blobs.

## Commit guidelines

Conventional commits — `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.
One agent or one schema per commit where possible; keep prompts and their tests
in the same commit.
