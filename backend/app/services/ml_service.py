"""
Trains and compares candidate scikit-learn models for regression or
classification targets, returning real evaluation metrics and feature
importance — used by the Predictive Analytics Agent.
"""

from __future__ import annotations
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_percentage_error, accuracy_score
from sklearn.preprocessing import OneHotEncoder
from app.models.prediction import ModelCandidate, FeatureImportance, ModelTask


def infer_task(series: pd.Series) -> ModelTask:
    if pd.api.types.is_numeric_dtype(series) and series.nunique() > 15:
        return ModelTask.REGRESSION
    return ModelTask.CLASSIFICATION


def _prepare_features(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, list[str]]:
    feature_df = df.drop(columns=[target]).copy()

    # Drop high-cardinality / likely-identifier text columns.
    for col in feature_df.columns:
        if feature_df[col].dtype == object and feature_df[col].nunique() > 50:
            feature_df = feature_df.drop(columns=[col])

    feature_df = feature_df.select_dtypes(include=["number", "object", "category", "bool"])
    feature_df = pd.get_dummies(feature_df, drop_first=True)
    feature_df = feature_df.fillna(feature_df.median(numeric_only=True)).fillna(0)
    return feature_df, feature_df.columns.tolist()


def train_candidates(
    df: pd.DataFrame, target: str, task: ModelTask | None = None
) -> tuple[list[ModelCandidate], list[FeatureImportance]]:
    working = df.dropna(subset=[target]).copy()
    if task is None:
        task = infer_task(working[target])

    X, feature_names = _prepare_features(working, target)
    y = working[target]

    if task == ModelTask.CLASSIFICATION:
        y = y.astype("category").cat.codes

    if len(X) < 20 or X.shape[1] == 0:
        return [], []

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    candidates: list[ModelCandidate] = []
    best_model = None
    best_score = -np.inf
    is_regression = task == ModelTask.REGRESSION

    model_specs = (
        [
            ("Linear Regression", LinearRegression()),
            ("Random Forest Regressor", RandomForestRegressor(n_estimators=150, random_state=42)),
            ("Gradient Boosted Trees", GradientBoostingRegressor(random_state=42)),
        ]
        if is_regression
        else [
            ("Logistic Regression", LogisticRegression(max_iter=1000)),
            ("Random Forest Classifier", RandomForestClassifier(n_estimators=150, random_state=42)),
        ]
    )

    for name, model in model_specs:
        start = time.time()
        model.fit(X_train, y_train)
        elapsed = round(time.time() - start, 2)
        predictions = model.predict(X_test)

        if is_regression:
            mape = mean_absolute_percentage_error(y_test, predictions)
            metric, score = "MAPE", round(float(mape), 4)
            comparison_score = -score  # lower MAPE is better
        else:
            acc = accuracy_score(y_test, predictions)
            metric, score = "Accuracy", round(float(acc), 4)
            comparison_score = score  # higher accuracy is better

        candidates.append(
            ModelCandidate(
                id=f"model_{len(candidates)+1}",
                name=name,
                task=task,
                metric=metric,
                score=score,
                training_time_seconds=elapsed,
                is_best=False,
            )
        )

        if comparison_score > best_score:
            best_score = comparison_score
            best_model = (model, len(candidates) - 1)

    if best_model is not None:
        candidates[best_model[1]].is_best = True

    feature_importance: list[FeatureImportance] = []
    winning_model = best_model[0] if best_model else None
    if winning_model is not None and hasattr(winning_model, "feature_importances_"):
        importances = winning_model.feature_importances_
        pairs = sorted(zip(feature_names, importances), key=lambda p: p[1], reverse=True)[:5]
        total = sum(v for _, v in pairs) or 1.0
        feature_importance = [
            FeatureImportance(feature=name, importance=round(float(v / total), 3)) for name, v in pairs
        ]
    elif winning_model is not None and hasattr(winning_model, "coef_"):
        coefs = np.abs(np.atleast_1d(winning_model.coef_).flatten())
        pairs = sorted(zip(feature_names, coefs), key=lambda p: p[1], reverse=True)[:5]
        total = sum(v for _, v in pairs) or 1.0
        feature_importance = [
            FeatureImportance(feature=name, importance=round(float(v / total), 3)) for name, v in pairs
        ]

    return candidates, feature_importance
