
# Vaelis — Production-ready General Intelligence Platform

This repository upgrades the original demo into a modular, production-oriented AI operating system called Vaelis. It uses a single configured AI model for all AI functionality and Tavily for optional web search ingestion.

**Highlights**
- Single-model AI core (configured via environment) for chat, reasoning, code, study, and document generation.
- Tavily for fresh web sources; the system consumes structured results (no fabricated citations).
- FastAPI backend with Firebase ID token verification and export endpoints (Markdown/PDF).
- Next.js (App Router) TypeScript frontend with Tailwind CSS, Firebase client, responsive UI and modes.

**Repository layout**
- `frontend/` — Next.js TypeScript app (App Router)
- `backend/` — FastAPI backend (single entrypoint: `backend/app.py`)
- `.env.example` — environment variables to set for local development
- `requirements.txt` — Python dependencies for backend services

Requirements and environment
- Python 3.10+ for backend; Node 18+ / npm for frontend.
- Create a `.env` or export environment variables. Required backend vars (names kept for compatibility):
  - `GEMINI_API_KEY` — API key for the configured AI model
  - `GEMINI_API_URL` — AI model API base URL
  - `TAVILY_API_KEY` — Tavily API key
  - `TAVILY_API_URL` — Tavily search endpoint
  - `FIREBASE_CREDENTIALS_JSON` — path to Firebase service account JSON for verifying tokens

Backend quick start
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="xxx"
export GEMINI_API_URL="https://your.ai.endpoint"
export TAVILY_API_KEY="yyy"
export TAVILY_API_URL="https://api.tavily.com/search"
export FIREBASE_CREDENTIALS_JSON="/path/to/service-account.json"
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Frontend quick start
```bash
cd frontend
npm install
npm run dev
```

Deploying

- Backend (Render):
  1. Add the required environment variables to Render: `GEMINI_API_KEY`, `GEMINI_API_URL`, `TAVILY_API_KEY`, `TAVILY_API_URL`, `FIREBASE_CREDENTIALS_JSON`, and `DATABASE_URL`.
  2. Create a new Web Service on Render and connect your repo. Render will use the `render.yaml` and `backend/Dockerfile` to build and run the `vaelis-backend` service. Ensure the `PORT` environment variable is set (Render provides one automatically).

- Frontend (Vercel):
  1. Create a new Vercel project linked to this repository.
  2. Set the environment variable `NEXT_PUBLIC_BACKEND_URL` to your backend URL (for example `https://vaelis-backend.onrender.com`).
  3. Deploy; Vercel will detect the Next.js app and build automatically.


Development notes
-- The frontend uses Firebase Auth (client-side) and sends the ID token in the `Authorization: Bearer <id-token>` header. The backend verifies tokens using `firebase-admin`.
-- All AI requests go through `backend/ai/service.py`, which calls the configured AI model and accepts structured `sources` from Tavily when `use_search` is enabled.
- Export endpoints are available at `/export/markdown/{conv_id}` and `/export/pdf/{conv_id}`.

Security & production notes
- Keep API keys and Firebase credentials out of source control; use a secrets manager in production.
- Serve the backend behind HTTPS and an API gateway; configure rate limits and monitoring.
- The backend sets strict security headers (CSP, X-Frame-Options) via middleware.

Next steps (recommended)
- Implement streaming (SSE or WebSocket) for progressive responses.
- Harden rate-limiting, request validation, and observability (metrics/logging).
- Complete frontend components: conversation history, streaming UI, export UX, and account pages.

If you want, I can continue and finish the remaining frontend pages (Recents, Settings), streaming client, and additional production artifacts (Docker Compose, CI).  
Further work (recommended)
