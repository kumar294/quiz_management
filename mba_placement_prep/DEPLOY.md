# Deployment

Two services: **Next.js frontend on Vercel**, **FastAPI backend on Render** with
managed Postgres.

## Backend (Render)

1. In Render → **New → Blueprint**, connect this repo. Render picks up
   `mba_placement_prep/render.yaml` and provisions:
   - `glim-prep-api` — Docker web service, `mba_placement_prep/backend/Dockerfile`
   - `glim-prep-db` — free Postgres, wired to the service via `DATABASE_URL`
2. Open the service → **Environment** → set `ANTHROPIC_API_KEY`.
3. First deploy runs automatically. Health check hits `/health`. Later pushes to
   `main` auto-deploy (`autoDeploy: true` in the blueprint).
4. Note the public URL, e.g. `https://glim-prep-api.onrender.com`.

## Frontend (Vercel)

1. In Vercel → **Add New → Project**, import this repo.
2. Set **Root Directory** to `mba_placement_prep/frontend`. Framework is
   auto-detected as Next.js; `vercel.json` there pins region `bom1` (Mumbai —
   closest to GLIM).
3. **Environment Variables** → add `NEXT_PUBLIC_API_BASE` pointing at the Render
   URL from the previous section.
4. Deploy. Every push to `main` deploys production; every PR gets a preview URL.

## Custom domain

Point `app.glim-prep.example` → Vercel and `api.glim-prep.example` → Render;
update `NEXT_PUBLIC_API_BASE` on Vercel and redeploy the frontend.

## CORS

Once the frontend runs on a different origin than the backend, allow it in
`backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ["FRONTEND_ORIGIN"]],
    allow_methods=["*"], allow_headers=["*"],
)
```

Add `FRONTEND_ORIGIN` to the Render service env vars.
