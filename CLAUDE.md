# GTM Copilot - Development Guide

## Architecture

- **Backend**: FastAPI (Python 3.12) — `backend/app/`
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS 4 — `frontend/src/`
- **GTM Scripts**: Python standard library only — `src/scripts/`
- **Containerization**: Docker Compose (dev: `docker-compose.yml`, prod: `docker-compose.prod.yml`)

## Quick Start

```bash
# Backend (dev)
cd backend
pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH="$(pwd):$(pwd)/../src/scripts" uvicorn app.main:app --reload --port 8000

# Frontend (dev)
cd frontend
npm install
npm run dev

# Docker
docker compose up --build
```

## Testing

```bash
# Backend tests
cd backend
PYTHONPATH="$(pwd):$(pwd)/../src/scripts" pytest --tb=short -q

# Backend linter
ruff check app/

# Frontend type check
cd frontend
npx tsc --noEmit
```

## Key Paths

| Path | Description |
|------|-------------|
| `backend/app/main.py` | FastAPI entry point |
| `backend/app/routers/` | API endpoints (auth, workspace, export, import, generate) |
| `backend/app/services/crawler.py` | Playwright-based site analysis |
| `backend/app/services/generator.py` | Claude AI GTM config generation |
| `backend/app/services/templates/prompts.py` | LLM prompt templates |
| `frontend/src/app/generate/page.tsx` | Main generation UI page |
| `frontend/src/lib/api.ts` | API client |
| `frontend/src/lib/types.ts` | Shared TypeScript types |
| `src/scripts/` | Core GTM client, auth, export/import CLI tools |
| `src/.env` | Environment variables (not committed) |

## Conventions

- Backend: Python, ruff for linting, pytest for tests
- Frontend: TypeScript strict, types exported from `@/lib/types`
- API responses use structured error format: `{ detail: string, type: string }`
- Environment config via pydantic-settings (see `backend/app/config.py`)
- GTM items always have `name` and `type` fields

## Environment Variables

See `src/.env.example` for all available options.
