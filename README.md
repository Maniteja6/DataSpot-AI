# DataSpot-AI# DataSpot AI

A RAG-powered AI data analyst. Upload a CSV/Excel dataset and a multi-stage LangGraph agent pipeline profiles, cleans, analyzes, forecasts, and generates decision recommendations — indexing every stage's output as it completes so a chat assistant can answer questions grounded in that dataset's actual analysis, not a generic LLM guess.

```
$ uvicorn app.main:app --reload
DataSpot AI Backend
Environment: local  |  AWS configured: false  |  S3 configured: false
Agent runtime: local deterministic (set BEDROCK_DIRECT_INVOKE=true for real Claude narration)
Vector store: local_faiss
✓ Ready → http://localhost:8000

$ curl -s localhost:8000/api/v1/chat -d '{"datasetId":"ds_8f2","message":"which region is dragging down revenue?"}'
{
  "answer": "West region revenue has declined 18% over the last 6 weeks, driven by a drop in units per order (see forecast + decision stages)...",
  "sources": ["forecast_summary", "decision_recommendations"],
  "queryUsed": null
}
```

## Features

- **LangGraph pipeline** — `validate → clean → analyze → predict → decide → summarize → index`, run as a background task per upload while the frontend polls status.
- **Graceful AWS degradation** — every AWS-backed capability (LLM reasoning, embeddings, vector store, object storage) has a local, zero-config fallback chosen automatically at runtime. Boots and runs fully offline with no cloud account.
- **Agent runtime abstraction** — every agent narrates through one shared method that routes to a deployed AgentCore Runtime → direct Bedrock `Converse` invocation → a local deterministic templating engine, in priority order. Agents never touch the AWS SDK directly.
- **RAG-grounded chat** — each pipeline stage's output is chunked and indexed into the vector store immediately after that stage completes, so the chat assistant is grounded in partial analysis before the full pipeline finishes.
- **Raw-data query escape hatch** — when retrieved facts don't cover a question, the chat agent emits a structured "I need a live query" signal; the SQL is validated (read-only, single statement, blocklisted keywords) and run against an in-memory DuckDB engine over the dataset's own dataframe.
- **Pluggable vector store** — local FAISS (numpy cosine-similarity fallback if FAISS isn't installed), OpenSearch Serverless, or a Bedrock Knowledge Base (Aurora PostgreSQL + pgvector), swapped with one setting.
- **Forecasting** — scikit-learn / statsmodels Holt-Winters by default, with an optional Prophet upgrade.
- **Decisions + export** — decision cards with scenario modeling, and export to CSV, JSON, Excel, PDF, or PPTX.
- **Session-scoped datasets, no auth** — a per-browser session id scopes what's visible in a shared demo deployment; it's a UX convenience, not a security boundary.

## Architecture

```
DataSpot-AI/
├── backend/app/
│   ├── agents/          # One class per pipeline stage (understanding, cleaning, analytics,
│   │                     BI, predictive, decision support, executive summary)
│   ├── agentcore/        # AgentCore-shaped scaffolding: action groups, gateway, memory, identity
│   ├── orchestrators/     # LangGraph pipeline graph, agent router, RAG orchestrator
│   ├── rag/              # Embeddings, chunking/indexing, retrieval, pluggable vector stores
│   ├── api/v1/           # FastAPI controllers (datasets, insights, predictive, chat, decisions, export...)
│   ├── repositories/      # Flat-file JSON persistence (no database)
│   └── services/          # Business logic: cleaning, analytics, forecasting, export
└── frontend/
    ├── app/(main)/        # One route per surface: dashboard, chat, data-insights, predictive-analysis...
    ├── features/          # Feature-scoped hooks & components
    └── services/          # One module per backend resource, live API first, mock data as fallback
```

**Query flow:** upload → LangGraph runs each pipeline stage's agent against the dataset → that stage's output is built into a retrieval document and indexed immediately → chat assistant retrieves relevant stage documents (falling back to a live DuckDB query over the raw rows when retrieval can't answer) → the active agent runtime narrates the response.

## Getting started

**Prerequisites:** Python 3.11+, Node 18+. No AWS account required.

```bash
# backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`, upload a CSV/Excel file, and watch the pipeline run.

## API

All routes are prefixed `/api/v1`; interactive docs at `/docs`.

| Resource | Routes |
|---|---|
| Datasets | `POST /datasets/upload`, `GET /datasets`, `GET /datasets/{id}`, `DELETE /datasets/{id}` |
| Insights | `GET /insights`, `GET /insights/{id}/correlations`, `GET /insights/{id}/columns` |
| Predictive | `GET /predictive/{id}`, `POST /predictive/{id}/train` |
| Data quality | `GET /data-quality/{id}`, `GET /data-quality/{id}/issues` |
| Decisions | `GET /decisions`, `PUT /decisions/{id}`, `POST /decisions/{id}/scenario` |
| Chat | `POST /chat`, `GET /chat/{conversation_id}/history` |
| Export | `POST /export`, `GET /export/download/{filename}` |
| Agents | `GET /agents/definitions`, `GET /agents/pipeline-status` |

## Configuration

Everything AWS-related is optional — unset means "use the local substitute." Full annotated list in `backend/.env.example`.

```bash
BEDROCK_DIRECT_INVOKE=false        # true + AWS creds -> real Claude narration via Bedrock Converse
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
VECTOR_STORE_PROVIDER=local_faiss  # local_faiss | opensearch | bedrock_kb
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
S3_BUCKET_NAME=                    # empty -> uploaded datasets stored on local disk
```

Switching `VECTOR_STORE_PROVIDER` mid-project isn't free: local hashing-based embeddings and real Bedrock embeddings have different dimensionality, so a provider switch means rebuilding the local index (re-run the pipeline per dataset). The two AWS-backed providers raise on misconfiguration rather than silently falling back to local.

## Why I built this

RAG demos are easy to fake with a hardcoded vector DB and one happy-path query. The interesting part of this project was making retrieval, agent orchestration, and forecasting all work identically whether AWS is configured or not — so the same pipeline code that runs a laptop demo is exactly what runs in production, just with real embeddings and a real Claude call swapped in underneath.

## Tech stack

Python · FastAPI · LangGraph / LangChain · pandas / DuckDB · scikit-learn / statsmodels · FAISS · AWS Bedrock (AgentCore, Converse API, Titan embeddings) · Next.js 15 · TypeScript · Tailwind · TanStack Query · Zustand

## Testing

```bash
cd backend && pytest              # real TestClient against the real app, no mocking
cd frontend && npm run lint && npm run typecheck
```

## License

[MIT](./LICENSE)
