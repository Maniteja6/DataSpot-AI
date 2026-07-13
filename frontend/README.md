# DataSpot AI — Frontend

RAG-powered AI Data Analyst UI. Next.js 15 (App Router), React 19, TypeScript,
Tailwind CSS, Zustand, React Query, Recharts, AG Grid.

## Signature design concept
DataSpot AI's identity is built around a **radar "spot"** — the idea that the
product finds the signal in noisy data. The logo mark, loading states, and
KPI card hover effects all reference concentric rings and a single scan line
sweeping across a dark, deep-navy field, with one bright signal-green accent
color used sparingly and reserved amber/rose tones for anomalies and risk.

## Getting started

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

The app runs fully standalone with generated mock data
(`NEXT_PUBLIC_USE_MOCKS=true`) so you can explore every page before the
FastAPI + AWS Bedrock AgentCore backend is wired up. Once the backend is
running, set `NEXT_PUBLIC_USE_MOCKS=false` and point
`NEXT_PUBLIC_API_BASE_URL` at it — every service function in `services/*`
already calls the real endpoint first and only falls back to mock data if
that call fails.

## No authentication

This prototype intentionally ships without a login flow. `middleware.ts` is
a pass-through placeholder — add real auth before deploying beyond a demo.

## Structure

- `app/` — routes (App Router), grouped under `(main)` for the shared
  sidebar/topbar shell
- `components/` — `ui/` primitives, `layout/`, `charts/`, `data-grid/`,
  `upload/`, `skeletons/`, `shared/`
- `features/` — one folder per product area (dashboard, data-insights,
  predictive-analysis, data-quality, ai-insights, decision-making, export,
  datasets, projects, chat-assistant), each with its own `components/` and
  `hooks/`
- `stores/` — Zustand global state
- `services/` — typed API clients, each wrapping a live FastAPI call with a
  mock-data fallback (`services/mocks/mockData.ts`)
- `lib/`, `utils/`, `types/` — shared config, helpers, and TypeScript types
- `styles/themes.css` — design tokens (dark/light CSS variables)

## Deployment (Vercel)

```bash
npm run build
```

Set `NEXT_PUBLIC_API_BASE_URL` as an environment variable in the Vercel
project pointing at your deployed FastAPI/AgentCore backend.
