"""
Applies real cleaning operations to a raw DataFrame: deduplication,
missing-value imputation, and basic type coercion. Returns the cleaned
DataFrame plus a structured log of what was done (used both for the
Data Quality page and as RAG-indexed "cleaning log" content).
"""

from __future__ import annotations
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class CleaningLogEntry:
    operation: str
    column: str | None
    count: int
    detail: str


@dataclass
class CleaningResult:
    cleaned_df: pd.DataFrame
    log: list[CleaningLogEntry] = field(default_factory=list)


def clean_dataset(df: pd.DataFrame) -> CleaningResult:
    log: list[CleaningLogEntry] = []
    working = df.copy()

    # 1. Deduplicate
    before = len(working)
    working = working.drop_duplicates()
    removed = before - len(working)
    if removed:
        log.append(
            CleaningLogEntry(
                operation="deduplicate",
                column=None,
                count=removed,
                detail=f"Removed {removed} exact duplicate rows.",
            )
        )

    # 2. Impute missing values
    for col in working.columns:
        series = working[col]
        missing = int(series.isna().sum())
        if missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(series):
            fill_value = series.median()
            working[col] = series.fillna(fill_value)
            log.append(
                CleaningLogEntry(
                    operation="impute_numeric",
                    column=str(col),
                    count=missing,
                    detail=f"Filled {missing} missing values in '{col}' with the median ({fill_value:.2f}).",
                )
            )
        else:
            mode_series = series.mode(dropna=True)
            fill_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            working[col] = series.fillna(fill_value)
            log.append(
                CleaningLogEntry(
                    operation="impute_categorical",
                    column=str(col),
                    count=missing,
                    detail=f"Filled {missing} missing values in '{col}' with the most frequent value ('{fill_value}').",
                )
            )

    # 3. Standardize categorical casing (merges "west"/"West"/"WEST" style variants)
    for col in working.select_dtypes(include="object").columns:
        nunique_before = working[col].nunique(dropna=True)
        normalized = working[col].astype(str).str.strip()
        # Only fold case if that meaningfully reduces cardinality (avoids
        # mangling genuinely case-sensitive free-text columns).
        folded = normalized.str.lower()
        if folded.nunique() < nunique_before:
            case_map = normalized.groupby(folded).agg(lambda s: s.value_counts().idxmax())
            working[col] = folded.map(case_map)
            merged = nunique_before - folded.nunique()
            if merged > 0:
                log.append(
                    CleaningLogEntry(
                        operation="standardize_casing",
                        column=str(col),
                        count=merged,
                        detail=f"Merged {merged} casing variants in '{col}' into a single canonical value each.",
                    )
                )

    return CleaningResult(cleaned_df=working, log=log)
