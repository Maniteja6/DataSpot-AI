# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataSpot AI is a RAG-powered AI data analyst. A user uploads a tabular dataset (CSV/Excel), and a multi-stage agent pipeline profiles, cleans, analyzes, forecasts, and generates decision recommendations and an executive summary — with every stage's output indexed into a retrieval store so a chat assistant can answer natural-language questions grounded in that dataset's actual analysis.

The system is a two-service monorepo:
- **Backend** — FastAPI + LangGraph orchestration layer, designed around AWS Bedrock AgentCore concepts (agents, action groups, memory, gateway) but runnable fully offline.
- **Frontend** — Next.js 15 App Router dashboard.

The defining architectural property of this codebase is **graceful AWS degradation**: every AWS-backed capability (LLM reasoning, embeddings, vector storage, object storage) has a local, zero-config substitute selected automatically at runtime based on which environment variables are set. The app boots and functions end-to-end on a laptop with no cloud account, and upgrades piece-by-piece to real AWS services as configuration is added — never as a code branch the developer has to opt into by hand.

## Commands

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000    # or any free port
pytest                                        # full suite (real TestClient, no app mocking)
pytest -k some_test                           # single test
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev         # dev server, http://localhost:3000
npm run build        # production build
npm run lint
npm run typecheck    # tsc --noEmit
```

Frontend talks to the backend via an API base URL environment variable (defaults to `http://localhost:8000` locally). There is no single root-level command that starts both — run each dev server in its own terminal.

## Backend Architecture

### Pipeline orchestration
A LangGraph state graph, run synchronously as a background task after upload (so the upload endpoint returns immediately while the frontend polls pipeline status), executes:

```
validate & profile -> clean -> analyze -> predict -> decide -> summarize -> index
```

Each stage invokes one or more agents, persists results through a repository layer, and — from the analysis stage onward — immediately builds a retrieval document from that stage's output and indexes it into the vector store. This means the chat assistant becomes grounded in a dataset's partial analysis before the full pipeline finishes, not only after.

### Agent runtime abstraction
Every agent narrates its findings through a shared base-agent method that builds a structured prompt (instruction + a bulleted facts section) and forwards it to whichever runtime is currently active, in priority order:

1. **A fully deployed Bedrock AgentCore Runtime** — used only if a real runtime endpoint is configured. Not currently deployed in any environment this project runs in.
2. **Direct Bedrock model invocation** — calls a Claude model's Converse API directly, enabled by a feature flag. This is the active path in every environment with real AWS credentials — real LLM narration without the cost or operational overhead of standing up a managed agent runtime.
3. **A local deterministic runtime** — the default with no AWS configuration. Turns the structured prompt into flowing prose via template rules, with zero external calls. Every agent's output is already grounded in real numbers computed by the service layer; this runtime only skips LLM-based phrasing.

Agents are written once against this interface and never call the AWS SDK directly — do not special-case runtime selection inside an agent.

### RAG subsystem
- **Vector store selection** is driven by a provider setting, chosen automatically or explicitly:
  - **Local (default)** — an on-disk vector index, using a real similarity-search library if installed, otherwise a pure-Python cosine-similarity fallback. Fully local, zero setup.
  - **OpenSearch Serverless** — a managed AWS vector search backend.
  - **A real Bedrock Knowledge Base**, backed by Aurora PostgreSQL Serverless v2 + pgvector. Ingestion here is asynchronous (write to object storage, then trigger a sync job), unlike the synchronous local/OpenSearch paths — a freshly indexed document is not immediately queryable through this provider.
  - The two AWS-backed providers are explicit, deliberate choices: if construction fails, the store raises rather than silently falling back to the local index, so misconfiguration is never masked as "it's just using the local index."
- **Embeddings** use a real Bedrock embedding model whenever AWS is reachable, otherwise a lightweight local hashing-based fallback. The two approaches produce vectors of different dimensionality and cannot coexist in the same index — switching embedding backends requires rebuilding the local vector index from scratch (re-run the pipeline per dataset).
- **Document scope** — indexed documents only ever come from aggregate stage output (profile, cleaning log, analytics summary, forecast summary, decision recommendations, executive summary). They never contain raw column values, so retrieval alone cannot answer questions like "list all distinct values of column X."
- **Raw-data query tool** — the escape hatch for exactly that gap. The chat agent's prompt asks the model to respond with a structured "I need a live query" signal (including the SQL) when retrieved facts don't cover the question but a query against the actual rows would. That SQL is validated (read-only, single statement, destructive-keyword blocklist) and executed against an in-memory analytical-SQL engine over the dataset's own dataframe — no other tables, files, or network access reachable from that connection. Query failures are handled deterministically (a plain string, not another LLM call) rather than asking the model to interpret an error it can only guess at.

### Storage & repositories
No database. Application state (dataset registry, predictive run history, requirement run history, etc.) persists to flat JSON files on disk, and uploaded dataset files are written to local disk unless object storage is configured, in which case they go to the cloud bucket instead. **These local JSON registries and uploaded files are git-tracked**, which means running the pipeline or the test suite locally mutates files git will want to commit. Check working-tree status before committing after any local testing, and avoid committing incidental local test data alongside real feature changes.

### Dataset isolation
There is no authentication. The frontend generates a random per-browser session identifier on first visit and sends it as a project ID on every dataset; the backend filters the dataset list by it. This is a UX convenience so concurrent visitors don't see each other's uploads in a shared demo deployment — it is not a security boundary. Fetching a single dataset by ID has no ownership check; a known dataset ID is fetchable directly.

## Frontend Architecture

Next.js 15 App Router, with one route per major surface (dashboard, dataset list/detail, chat, data insights, predictive analysis, data quality, AI insights, decision making, export, projects, settings). Feature code (data-fetching hooks, feature-scoped components) is organized separately from route files, grouped by feature rather than by file type.

- **Service layer** — one module per backend resource, each function wrapped in a shared mock-fallback helper. A build-time flag can force mock data unconditionally; otherwise the live API call runs first and mock data is only a fallback if it fails. **This fallback helper catches every error indiscriminately**, including legitimate "not found" responses — several past bugs in this codebase were exactly this: a genuine empty/not-found state getting silently repainted as mock data instead of a real empty state. When adding a new service call for a case where "not found" is an expected, meaningful state (not a real outage), prefer a variant that returns null on that response rather than routing through the mock fallback.
- **Same-origin proxy route** — a pass-through proxy to the FastAPI backend, for environments (e.g. some hosting preview setups) where direct cross-origin calls are restricted.
- **Dataset selection** — a shared dropdown component used consistently across every page that operates on a single dataset. Do not hardcode a fallback dataset ID in a page — a stale hardcoded ID producing a "not found" response is exactly the failure mode the mock-fallback helper turns into confusing mock-data regressions. Prefer no selection plus an explicit "no dataset yet" empty state.
- **State** — a server-state query library for anything backend-derived, plus a small client-state store for local UI state.

## Configuration

Every AWS-related environment variable is optional and additive — unset means "use the local substitute," never a required setup step for basic functionality. When adding a new AWS-backed capability, follow this same pattern: a settings field, a runtime check for whether it's configured, and a local fallback path that keeps the pipeline fully functional without it. Do not make a new feature depend on AWS being configured without an equivalent offline path.

Key configuration concepts:
- A feature flag that enables real Claude narration via direct Bedrock invocation (see runtime priority above).
- A vector-store provider selector (local / OpenSearch / Bedrock Knowledge Base).
- An object-storage bucket setting — unset uses local disk storage for uploaded datasets.
- An AgentCore runtime endpoint setting — only relevant if a full AgentCore Runtime is ever deployed; leave unset otherwise.

## Deployment

- **Backend** — deployed as a Python web service, health-checked at a dedicated endpoint. Production runs with direct Bedrock invocation enabled and the local vector store provider.
- **Frontend** — deployed as a standard Next.js build on a static/edge hosting platform.
- Deeper AWS setup notes (model access, IAM policies, Aurora/pgvector, OpenSearch Serverless) live in the infrastructure directory as documentation and IaC templates — these describe infrastructure the developer provisions manually; nothing in the application code runs a deploy/provision command automatically.

## Working in This Repository

- **Verify against the running app, not just the code.** Bugs in this codebase have repeatedly been the kind that only reproduce against real requests — a dataframe used in a truthiness expression raising an error, a broad exception handler masking a "not found" as an outage, an embedding-dimension mismatch that only shows up once real vectors are compared against stale ones. Prefer a real request against the locally running backend, or a real browser check for frontend changes, over reasoning from the code alone.
- **Don't let local test/dev runs pollute what gets committed.** The test suite runs against the real app and writes to the git-tracked local registries and upload directory. Check working-tree status before staging, and revert any of those tracked files that a local run touched with synthetic data unrelated to the change being made.
- **Treat AWS integration work as two-phase**: code, infrastructure-as-code templates, and docs can be written and committed freely — they cost nothing and touch no live infrastructure. Actually provisioning billable AWS resources (creating a cluster, enabling a model, standing up a Knowledge Base) is a separate, explicit step handed to the person running this project as exact commands/console steps, not executed automatically.
- **For larger or costlier changes** (a new AWS service dependency, a schema/data-model change, anything with a real cost or migration tradeoff), lay out the options and their tradeoffs before implementing, rather than picking one silently.
