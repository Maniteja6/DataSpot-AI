from __future__ import annotations
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.agentcore.action_groups.dataset_actions import profile_and_clean
from app.services.cleaning_service import CleaningResult


class DatasetUnderstandingAgent(BaseAgent):
    agent_name = "dataset_understanding"

    def run(self, dataset: Dataset) -> tuple[Dataset, CleaningResult, str]:
        dataset, cleaning_result = profile_and_clean(dataset)

        type_counts: dict[str, int] = {}
        for c in dataset.columns:
            type_counts[c.data_type.value] = type_counts.get(c.data_type.value, 0) + 1
        type_summary = ", ".join(f"{v} {k}" for k, v in type_counts.items())

        facts = [
            f"Dataset '{dataset.name}' has {dataset.row_count} rows and {dataset.column_count} columns",
            f"Column types detected: {type_summary}",
            f"Overall data quality score is {dataset.quality_score} out of 100",
        ]
        narrative = self.narrate(
            "Summarize what this dataset contains and its overall shape for a business analyst.",
            facts,
            dataset_id=dataset.id,
        )
        return dataset, cleaning_result, narrative
