"""
Action group backing the Dataset Understanding and Data Cleaning agents.
In a real Bedrock AgentCore deployment these functions are registered as
the action group's tool schema; the local agent runtime calls them
directly (see app/agents/dataset_understanding_agent.py and
data_cleaning_agent.py).
"""

from __future__ import annotations
from app.models.dataset import Dataset
from app.services import dataset_service, profiling_service
from app.services.cleaning_service import clean_dataset, CleaningResult


def get_dataset_summary(dataset: Dataset) -> dict:
    """Tool: returns the current schema/profile summary for a dataset."""
    return {
        "name": dataset.name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns": [c.model_dump() for c in dataset.columns],
    }


def profile_and_clean(dataset: Dataset) -> tuple[Dataset, CleaningResult]:
    """
    Tool: loads the raw file, cleans it, profiles the result, and updates
    the Dataset record + cleaned-DataFrame cache. This is the concrete work
    behind both the Dataset Understanding and Data Cleaning agents.
    """
    raw_df = dataset_service.load_raw_dataframe(dataset)
    cleaning_result = clean_dataset(raw_df)
    cleaned_df = cleaning_result.cleaned_df

    columns = profiling_service.profile_columns(cleaned_df)
    duplicate_rows = profiling_service.count_duplicates(raw_df)
    missing_cells = profiling_service.count_missing_cells(raw_df)
    outlier_count = profiling_service.count_outliers(cleaned_df)
    total_cells = raw_df.shape[0] * raw_df.shape[1] if raw_df.shape[0] else 0
    quality_score = profiling_service.compute_quality_score(
        row_count=len(raw_df),
        duplicate_rows=duplicate_rows,
        missing_cells=missing_cells,
        total_cells=total_cells,
        outlier_count=outlier_count,
    )

    dataset.row_count = len(cleaned_df)
    dataset.column_count = len(cleaned_df.columns)
    dataset.columns = columns
    dataset.duplicate_rows = duplicate_rows
    dataset.missing_cells = missing_cells
    dataset.outlier_count = outlier_count
    dataset.quality_score = quality_score

    dataset_service.set_cleaned_dataframe(dataset.id, cleaned_df)
    return dataset, cleaning_result
