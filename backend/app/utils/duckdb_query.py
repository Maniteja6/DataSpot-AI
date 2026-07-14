"""
Thin DuckDB helper used by analytics_service for fast, SQL-expressed
aggregations over a cleaned dataset without standing up a real warehouse —
DuckDB queries the pandas DataFrame directly (zero-copy where possible).
"""

from __future__ import annotations
import duckdb
import pandas as pd


def query_dataframe(df: pd.DataFrame, sql: str, table_name: str = "dataset") -> pd.DataFrame:
    con = duckdb.connect(database=":memory:")
    try:
        con.register(table_name, df)
        return con.execute(sql).fetchdf()
    finally:
        con.close()


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()
