# Contributing

## Commit style

Conventional commits:

```
feat(agents): add gap-analysis agent
fix(orchestration): parallelize resume + gap steps
docs(readme): document RQ1/RQ2 metrics
test(schemas): cover PrepPlan roundtrip
chore(ci): pin python 3.11
```

One agent or schema per commit where possible. Prompt changes ship with the
test that exercises them.

## Adding an agent

1. Write the system prompt in `backend/app/prompts/<name>.md`.
2. Add the input/output schema to `backend/app/schemas/domain.py`.
3. Add the async wrapper to `backend/app/agents/__init__.py` via `run_agent`.
4. Wire it into `backend/app/orchestration/graph.py`.
5. Cover the schema with a roundtrip test in `backend/tests/`.
6. Add a golden-input fixture under `backend/tests/fixtures/<name>/` for
   integration testing against a recorded Claude response.

## Do not

- Fabricate resume experience, interview questions, or citations. Every agent
  prompt says so — keep it that way.
- Scrape sources that forbid it or without the throttle set in `services/scrapers`.
- Store PII outside the DB row for the owning student.
