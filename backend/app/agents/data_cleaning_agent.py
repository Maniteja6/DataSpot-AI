from __future__ import annotations
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.services.cleaning_service import CleaningResult


class DataCleaningAgent(BaseAgent):
    agent_name = "data_cleaning"

    def run(self, dataset: Dataset, cleaning_result: CleaningResult) -> str:
        if not cleaning_result.log:
            return f"No cleaning operations were necessary for '{dataset.name}' — the data arrived in good shape."

        facts = [entry.detail for entry in cleaning_result.log]
        return self.narrate(
            "Summarize the data cleaning operations performed on this dataset and why they matter.",
            facts,
            dataset_id=dataset.id,
        )
