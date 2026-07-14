from __future__ import annotations
from app.agents.base_agent import BaseAgent
from app.rag.schemas.rag_schema import RagAnswer
from app.agentcore.action_groups.rag_actions import retrieve_context


class RagChatAgent(BaseAgent):
    agent_name = "rag_chat"

    def run(self, question: str, dataset_id: str | None) -> RagAnswer:
        context = retrieve_context(question, dataset_id, top_k=5)

        if not context.chunks:
            answer = self.narrate(
                f"Answer the analyst's question as best you can: '{question}'. "
                "No indexed context is available yet, so say so plainly and suggest "
                "uploading/processing a dataset first.",
                ["No retrieved context is available for this dataset yet"],
            )
            return RagAnswer(answer=answer, citations=[], retrieved_chunks=[])

        facts = [f"[{c.source.type.value}] {c.text}" for c in context.chunks]
        answer = self.narrate(
            f"Answer the analyst's question using only the retrieved context: '{question}'.",
            facts,
            dataset_id,
        )
        return RagAnswer(answer=answer, citations=context.citations, retrieved_chunks=context.chunks)
