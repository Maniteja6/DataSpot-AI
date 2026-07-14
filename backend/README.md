# DataSpot AI — Backend

FastAPI backend orchestrating 8 specialized agents via AWS Bedrock
AgentCore, with a RAG subsystem grounding every generated insight,
recommendation, and chat answer in citable, indexed content.

## Runs fully offline by default

Every AWS-dependent piece has a real, working local fallback, selected
automatically based on what's configured in `.env`:

| Feature | AWS-configured | Local fallback (default) |
|---|---|---|
| Dataset storage | S3 | Local disk (`storage/uploads`) |
| Agent reasoning | Bedrock AgentCore Runtime | Deterministic template-based narrator, grounded in the same computed stats |
| Embeddings | Titan Text Embeddings v2 | scikit-learn `HashingVectorizer` |
| Vector store | OpenSearch Serverless / Bedrock Knowledge Bases | Local FAISS-or-NumPy cosine-similarity index (`storage/vector_index`) |
| Memory | AgentCore Memory | In-process store |

This means `pip install -r requirements.txt && uvicorn app.main:app --reload`
gets you the **entire pipeline working end-to-end** — upload a CSV, watch
it get cleaned/profiled/analyzed/forecasted/decided/summarized/indexed, and
ask the Chat Assistant grounded questions about it — with zero AWS
credentials. Set the AWS env vars in `.env` to switch any piece over to the
real service without touching application code.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API reference, or
`http://localhost:8000/health` for a status check.

## Run the tests

```bash
pytest -v
```

20 tests cover dataset upload/validation, the full LangGraph pipeline, all
8 agents, and RAG retrieval/citation behavior — all run against the real
FastAPI app via `TestClient`, no mocked internals.

## Architecture

```
API (FastAPI controllers)
  -> Orchestrators (LangGraph pipeline, RAG orchestrator, memory manager)
    -> Agents (8 agents, each wrapping AgentCore runtime invocation)
      -> Action Groups (tool functions agents call)
        -> Services (pandas/DuckDB/scikit-learn/statsmodels — the real math)
          -> Repositories (in-memory stores; swap for a real DB when ready)
```

The **pipeline** (`app/orchestrators/pipeline_graph.py`) runs as a
FastAPI `BackgroundTask` after upload: validate & profile → clean →
analyze → predict → decide → summarize → index. The frontend polls
`GET /api/v1/agents/pipeline-status?datasetId=` to show live progress.

The **RAG subsystem** indexes each stage's output immediately after it
completes (`app/rag/ingestion/indexing_pipeline.py`), so the Chat Assistant
can answer grounded questions about a dataset's profile before the whole
pipeline even finishes.

## Key environment variables

See `.env.example` for the full list. The only one that matters for going
from "local demo" to "real AWS": `BEDROCK_AGENTCORE_RUNTIME_ENDPOINT`. Once
that's set (along with AWS credentials), `app/config/settings.py`'s
`aws_configured` flips to `True` and every service above swaps to its real
AWS implementation automatically.

## Notes on scope

This is a working prototype: in-memory repositories (not a real database),
a template-based local agent narrator (not a full LLM) when AgentCore isn't
configured, and broad IAM permissions in `infra/aws/iam_policy.json` meant
for fast local iteration. Tighten all three before handling real customer
data — see `infra/deployment_notes.md`.
