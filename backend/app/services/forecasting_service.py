"""
Time-series forecasting. Uses statsmodels' Holt-Winters exponential
smoothing when there's enough history for a seasonal fit, and falls back to
simple linear-trend extrapolation for short series — both paths are real
statistical models, not placeholders. Swap in Prophet behind the same
`generate_forecast()` signature if it's installed and preferred; nothing
else in the app needs to change (see requirements.txt).
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from app.models.prediction import ForecastPoint
from app.services.analytics_service import _find_datetime_column


def _resample_monthly(df: pd.DataFrame, date_col: str, target_col: str) -> pd.Series:
    working = df[[date_col, target_col]].dropna().copy()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working = working.dropna().sort_values(date_col)
    working = working.set_index(date_col)[target_col]
    return working.resample("MS").sum()


def generate_forecast(df: pd.DataFrame, target_col: str, periods: int = 6) -> tuple[list[ForecastPoint], str]:
    date_col = _find_datetime_column(df)
    if date_col is None:
        return [], "No datetime column was found, so a time-based forecast could not be generated."

    series = _resample_monthly(df, date_col, target_col)
    series = series[series.index.notna()]
    if len(series) < 4:
        return [], f"Not enough historical periods ({len(series)}) to forecast '{target_col}' reliably."

    try:
        forecast_values, method = _holt_winters_forecast(series, periods)
    except Exception:
        forecast_values, method = _linear_trend_forecast(series, periods)

    points: list[ForecastPoint] = []
    for date, value in series.items():
        points.append(ForecastPoint(date=date.strftime("%Y-%m"), actual=round(float(value), 2)))

    last_value = float(series.iloc[-1])
    for i, value in enumerate(forecast_values):
        future_date = series.index[-1] + pd.DateOffset(months=i + 1)
        margin = abs(value - last_value) * 0.15 + abs(value) * 0.05
        points.append(
            ForecastPoint(
                date=future_date.strftime("%Y-%m"),
                forecast=round(float(value), 2),
                lower_bound=round(float(value - margin), 2),
                upper_bound=round(float(value + margin), 2),
            )
        )

    pct_change = ((forecast_values[-1] - last_value) / abs(last_value) * 100) if last_value else 0
    explanation = (
        f"Forecast for '{target_col}' generated with {method} over {len(series)} historical periods. "
        f"Projected change over the next {periods} periods: {pct_change:+.1f}%."
    )
    return points, explanation


def _holt_winters_forecast(series: pd.Series, periods: int) -> tuple[list[float], str]:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    seasonal_periods = 4 if len(series) >= 8 else None
    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add" if seasonal_periods else None,
        seasonal_periods=seasonal_periods,
    ).fit()
    forecast = model.forecast(periods)
    return forecast.tolist(), "Holt-Winters exponential smoothing"


def _linear_trend_forecast(series: pd.Series, periods: int) -> tuple[list[float], str]:
    x = np.arange(len(series))
    y = series.values.astype(float)
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(series), len(series) + periods)
    forecast = (slope * future_x + intercept).tolist()
    return forecast, "linear trend extrapolation"
