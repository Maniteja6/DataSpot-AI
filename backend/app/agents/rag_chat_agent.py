from __future__ import annotations
import json
import re
from app.agents.base_agent import BaseAgent
from app.agentcore.runtime_client import LocalDeterministicRuntime
from app.rag.schemas.rag_schema import RagAnswer, RagContext
from app.agentcore.action_groups.rag_actions import retrieve_context
from app.agentcore.action_groups.data_query_actions import run_dataframe_query
from app.repositories.dataset_repository import dataset_repository


def _clean_point(text: str) -> str:
    text = re.sub(r"\.{2,}", ".", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def _parse_raw_query_request(raw: str) -> str | None:
    """Returns the requested SQL if `raw` is a {"needsRawQuery": true, "sql":
    "..."} response, else None (meaning `raw` is just the final answer)."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    if isinstance(parsed, dict) and parsed.get("needsRawQuery") and isinstance(parsed.get("sql"), str):
        return parsed["sql"]
    return None


class RagChatAgent(BaseAgent):
    agent_name = "rag_chat"

    def run(self, question: str, dataset_id: str | None) -> RagAnswer:
        # A dataset is optional: when one is selected we retrieve grounded
        # context and cite it, but the assistant still answers general
        # questions (or questions the retrieved facts don't cover) using
        # its own knowledge rather than refusing outright.
        context = retrieve_context(question, dataset_id, top_k=5) if dataset_id else RagContext()
        facts = [c.text for c in context.chunks]

        if isinstance(self._runtime, LocalDeterministicRuntime):
            # No LLM configured — narrate() only paraphrases facts and drops
            # the question, so build a direct, scannable bullet list from
            # the retrieved facts when there are any.
            if facts:
                points = [_clean_point(f) for f in facts]
                answer = f'On "{question.strip()}":\n' + "\n".join(f"- {p}" for p in points)
            else:
                answer = self.narrate(
                    f"Answer the analyst's question as best you can: '{question}'.",
                    ["No dataset-specific context is available for this question"],
                )
        elif facts:
            # A real LLM is available and we have grounded context — prefer
            # it, but allow falling back to general knowledge for anything
            # the facts don't cover instead of refusing. Also offer a raw
            # data query escape hatch for questions the summary facts were
            # never designed to answer (distinct values, exact aggregates).
            dataset = dataset_repository.get(dataset_id) if dataset_id else None
            schema_block = ""
            if dataset:
                schema_block = "\n\nDATASET SCHEMA (table name: dataset):\n" + "; ".join(
                    f"{c.name} ({c.data_type.value})" for c in dataset.columns
                )

            raw_response = self.narrate(
                f"Answer EXACTLY what the analyst asked, no more. Question: '{question}'. "
                "Ground your answer in the retrieved facts below whenever they're relevant. "
                "If the facts don't fully cover the question, answer using your own general "
                "knowledge instead of refusing, and make clear which parts of your answer are "
                "specific to this dataset versus general knowledge. Match the requested scope "
                "and quantity precisely — if asked for one thing, give exactly one, not several. "
                "Do not add unrequested sections, sub-questions, caveats, or supporting context "
                "the analyst didn't ask for. Be as brief as the question allows."
                + (
                    "\n\nIf the facts above don't cover the question AND it needs exact raw data "
                    "(e.g. distinct values of a column, an exact count/median, specific rows) that "
                    "a SQL query against the dataset could answer, respond with ONLY this JSON "
                    '(no other text): {"needsRawQuery": true, "sql": "SELECT ..."}. '
                    f"Only SELECT queries are allowed.{schema_block}"
                    if dataset
                    else ""
                ),
                facts,
                dataset_id,
            )

            requested_sql = _parse_raw_query_request(raw_response) if dataset else None
            if requested_sql:
                succeeded, query_fact = run_dataframe_query(dataset, requested_sql)
                if succeeded:
                    answer = self.narrate(
                        f"Using the live query result below, answer the analyst's original "
                        f"question concisely: '{question}'.",
                        [query_fact],
                        dataset_id,
                    )
                else:
                    # Deterministic, not another LLM call — asking the model to
                    # interpret a failure string produced confusing answers
                    # (it once asked the analyst to supply the query result
                    # themselves instead of just reporting the failure).
                    answer = f"I couldn't answer that — {query_fact}."
            else:
                answer = raw_response
        else:
            # No LLM-usable context at all (no dataset selected, or nothing
            # indexed for it yet) — answer as a general-purpose assistant.
            answer = self.narrate(
                f"Answer EXACTLY what the analyst asked, no more, using your own general "
                f"knowledge: '{question}'. No dataset-specific context is available for this "
                "question, so don't claim the answer comes from any dataset. Match the "
                "requested scope and quantity precisely, and don't add unrequested sections "
                "or extra context.",
                [],
                dataset_id,
            )

        return RagAnswer(answer=answer, citations=context.citations, retrieved_chunks=context.chunks)
