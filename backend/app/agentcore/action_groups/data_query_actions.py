"""
Tool: lets the RAG Chat Agent answer questions that need the actual raw
dataset (distinct values, exact counts/medians, specific rows) rather than
only the pre-computed summary facts indexed during the pipeline. Built on
app/utils/duckdb_query.py's query_dataframe, which already sandboxes
execution to a single in-memory dataframe with no other tables or file/
network access — this module adds the validation and result-shaping layer
on top, and must never raise into the chat flow (a bad or failed query
should degrade to an honest error string, not a 500).
"""

from __future__ import annotations
import re
from app.models.dataset import Dataset
from app.services import dataset_service
from app.utils.duckdb_query import query_dataframe
from app.config.logging_config import get_logger

logger = get_logger(__name__)

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|attach|detach|copy|pragma|create|"
    r"export|import|call|install|load)\b",
    re.IGNORECASE,
)
_MAX_ROWS = 500
_MAX_FACT_CHARS = 4000


def run_dataframe_query(dataset: Dataset, sql: str) -> tuple[bool, str]:
    """Validates and runs `sql` against `dataset`'s actual rows. Returns
    (True, fact string) on success, or (False, plain explanation) on
    failure — the bool lets callers skip asking the LLM to interpret a
    failure it can only guess at, and answer deterministically instead.
    Never raises."""
    error = _validate_select_only(sql)
    if error:
        logger.warning("Rejected unsafe chat data query for dataset %s: %s", dataset.id, error)
        return False, f"that query wasn't allowed ({error.rstrip('.')})"

    try:
        df = dataset_service.get_cleaned_dataframe(dataset.id)
        if df is None:
            df = dataset_service.load_raw_dataframe(dataset)
    except Exception as exc:
        logger.warning("Could not load dataframe for dataset %s: %s", dataset.id, exc)
        return False, "the dataset's raw data couldn't be loaded"

    wrapped = f"SELECT * FROM ({sql.strip().rstrip(';')}) AS _sub LIMIT {_MAX_ROWS}"
    try:
        result = query_dataframe(df, wrapped)
    except Exception as exc:
        logger.warning("Chat data query failed for dataset %s: %s", dataset.id, exc)
        return False, f"the query failed to run ({exc})"

    return True, _format_result(result)


def _validate_select_only(sql: str) -> str | None:
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        return "only a single statement is allowed."
    if not re.match(r"(?is)^\s*select\b", stripped):
        return "only SELECT queries are allowed."
    if _FORBIDDEN_KEYWORDS.search(stripped):
        return "that query isn't allowed (read-only queries only)."
    return None


def _format_result(result) -> str:
    if result.empty:
        return "The query returned no rows."

    text = result.to_csv(index=False)
    if len(text) > _MAX_FACT_CHARS:
        truncated = result.head(50)
        text = truncated.to_csv(index=False) + f"\n(truncated — showing first {len(truncated)} of {len(result)} rows)"
    return f"Live query result:\n{text.strip()}"
