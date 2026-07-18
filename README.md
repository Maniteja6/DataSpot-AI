# DataSpot AI

Live App: https://dataspot.vercel.app

A RAG-powered AI data analyst agent. Upload a tabular dataset (CSV/Excel) and a multi-stage LangGraph pipeline profiles, cleans, analyzes, forecasts, and generates decision recommendations plus an executive summary — indexing every stage's output into a retrieval store as it completes, so a chat assistant can answer natural-language questions grounded in that dataset's own analysis instead of a generic LLM guess.

## Features

- Upload CSV or Excel (`.xlsx`) datasets
- Automated LangGraph pipeline: validate & profile → clean → analyze → predict → decide → summarize → index
- Data cleaning with a transparent, stage-by-stage cleaning report
- Data quality scoring and issue detection derived from the cleaning report
- EDA: profiling summaries, statistical description, correlations, column-level insights
- Forecasting: scikit-learn / statsmodels Holt-Winters baseline (Prophet as an optional upgrade)
- Decision recommendation cards with scenario modeling
- RAG-grounded chat assistant — retrieves from a vector index built from the pipeline's own analysis, with a raw-data query escape hatch (validated read-only SQL run against the dataset via DuckDB) for questions retrieval alone can't answer
- Export to CSV, JSON, Excel, PDF, or PPTX
- **Graceful AWS degradation** — every AWS-backed capability (Claude narration, embeddings, vector store, object storage) has a local, zero-config fallback chosen automatically at runtime; the app runs fully offline with no cloud account and upgrades piece-by-piece as AWS config is added
- Session-scoped datasets, no auth required — a per-browser session id scopes what's visible in a shared demo deployment

## Workflow

```
Upload (CSV / XLSX)
        ↓
Validate & profile
        ↓
Data cleaning + quality scoring
        ↓
Analytics (EDA, correlations, summaries)
        ↓
Predictive forecasting (optional target/metric)
        ↓
Decision recommendations + scenario modeling
        ↓
Executive summary
        ↓
Index into vector store → RAG chat assistant
        ↓
Export (CSV / JSON / Excel / PDF / PPTX)
```

Each stage indexes its output into the vector store immediately after it completes, so the chat assistant is grounded in partial analysis before the full pipeline finishes running.

## Tech stack

| Area | Libraries |
|---|---|
| Backend framework | FastAPI, Uvicorn, Pydantic |
| Orchestration | LangGraph, LangChain Core |
| Data processing | pandas, NumPy, PyArrow, DuckDB, openpyxl |
| ML / forecasting | scikit-learn, statsmodels (Prophet optional) |
| RAG / vector store | local FAISS (pure-NumPy cosine-similarity fallback if FAISS isn't installed), OpenSearch Serverless, or Bedrock Knowledge Base (Aurora PostgreSQL + pgvector) |
| LLM | AWS Bedrock — AgentCore Runtime / direct Claude `Converse` invocation / local deterministic template runtime |
| Export | ReportLab (PDF), python-pptx |
| Frontend | Next.js 15 (App Router), React 18, TypeScript |
| Frontend UI | Tailwind CSS, Radix UI, Framer Motion, Lucide, Recharts, AG Grid |
| Frontend state | TanStack Query, Zustand, React Hook Form + Zod |
| Testing | pytest + httpx (real `TestClient`, no app mocking), ESLint, `tsc` |

## Project structure

```
DataSpot-AI/
├── backend/
│   └── app/
│       ├── agents/          # One class per pipeline stage (understanding, cleaning,
│       │                      analytics, BI, predictive, decision support, exec summary, chat)
│       ├── agentcore/        # AgentCore-shaped scaffolding: action groups, gateway, memory, identity
│       ├── orchestrators/     # LangGraph pipeline graph, agent router, RAG orchestrator
│       ├── rag/              # Embeddings, ingestion/indexing, retrieval, pluggable vector stores
│       ├── api/v1/           # FastAPI controllers (datasets, insights, predictive, data-quality,
│       │                      decisions, chat, export, agents, projects, requirements)
│       ├── repositories/      # Flat-file JSON persistence (no database)
│       ├── services/          # Business logic: cleaning, profiling, analytics, forecasting, ML, export
│       ├── models/ schemas/ config/ middleware/
│       └── main.py
├── frontend/
│   └── app/(main)/            # One route per surface: dashboard, datasets, chat-assistant,
│                                data-insights, predictive-analysis, data-quality, ai-insights,
│                                decision-making, export, projects
│       ├── features/          # Feature-scoped hooks & components
│       ├── services/          # One module per backend resource, live API first, mock data as fallback
│       └── stores/            # Zustand client state
└── infra/                     # AWS IaC templates & deployment notes (Aurora/pgvector, OpenSearch, IAM)
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- No AWS account required for local/offline use

## Installation

```bash
git clone <your-repo-url>
cd DataSpot-AI
```

Backend:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment (Windows PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Frontend (separate terminal):

```bash
cd frontend
npm install
```

## Configuration

Backend — copy `backend/.env.example` to `backend/.env`. Everything AWS-related is optional; unset means "use the local substitute":

```bash
BEDROCK_DIRECT_INVOKE=false        # true + AWS creds -> real Claude narration via Bedrock Converse
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
VECTOR_STORE_PROVIDER=local_faiss  # local_faiss | opensearch | bedrock_kb
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
S3_BUCKET_NAME=                    # empty -> uploaded datasets stored on local disk
```

Frontend — copy `frontend/.env.local.example` to `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCKS=False
```

Switching `VECTOR_STORE_PROVIDER` mid-project isn't free: local hashing-based embeddings and real Bedrock embeddings differ in dimensionality, so a provider switch means rebuilding the local vector index (re-run the pipeline per dataset). The two AWS-backed providers raise on misconfiguration rather than silently falling back to the local index.

## Run the application

```bash
# backend
cd backend
uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm run dev
```

Open `http://localhost:3000`, upload a CSV/Excel file, and watch the pipeline run stage by stage. Interactive API docs are available at `http://localhost:8000/docs`.

## Example use case

Upload something like a retail sales or Titanic-style dataset. The pipeline profiles and cleans it, scores data quality, runs EDA and correlation analysis, trains a baseline forecast, and produces decision cards and an executive summary — all indexed as it goes. Then ask the chat assistant something like *"which region is dragging down revenue?"* and get an answer grounded in the actual forecast and decision-stage output, with sources cited.

## Project goals

- Demonstrate a production-shaped, multi-agent RAG pipeline that runs identically offline and on AWS
- Show that retrieval, agent orchestration, and forecasting can share one codebase with zero cloud-specific branches
- Combine deterministic analytics (real computed numbers) with LLM-generated narration and interpretation
- Ground a conversational assistant in a dataset's own analysis rather than general LLM knowledge

## Testing

```bash
cd backend && pytest              # real TestClient against the real app, no mocking
cd frontend && npm run lint && npm run typecheck
```

## License

[MIT](./LICENSE)
