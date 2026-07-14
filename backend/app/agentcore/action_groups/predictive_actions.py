"""
Action group backing the Predictive Analytics agent.
"""

from __future__ import annotations
import pandas as pd
from app.models.prediction import PredictiveRun, ModelTask
from app.services.ml_service import train_candidates, infer_task
from app.services.forecasting_service import generate_forecast


def train_and_evaluate_models(
    dataset_id: str, df: pd.DataFrame, target: str, task: ModelTask | None = None
) -> PredictiveRun:
    """Tool: trains candidate models for `target`, and if it's a numeric
    column with a datetime column present, also produces a forecast."""
    resolved_task = task or infer_task(df[target])
    candidates, feature_importance = train_candidates(df, target, resolved_task)

    forecast_points: list = []
    explanation = ""
    if resolved_task == ModelTask.REGRESSION:
        forecast_points, forecast_explanation = generate_forecast(df, target)
        if forecast_points:
            explanation = forecast_explanation
            resolved_task = ModelTask.FORECASTING

    if not explanation:
        best = next((c for c in candidates if c.is_best), None)
        if best:
            explanation = (
                f"{best.name} was selected with the best {best.metric} ({best.score}) "
                f"among {len(candidates)} candidates evaluated."
            )
        else:
            explanation = "Not enough data was available to train a reliable model for this target."

    return PredictiveRun(
        dataset_id=dataset_id,
        target=target,
        task=resolved_task,
        candidates=candidates,
        feature_importance=feature_importance,
        forecast=forecast_points,
        explanation=explanation,
    )
