from __future__ import annotations
import re
from app.agents.base_agent import BaseAgent
from app.agentcore.runtime_client import LocalDeterministicRuntime
from app.rag.schemas.rag_schema import RagAnswer
from app.agentcore.action_groups.rag_actions import retrieve_context


def _clean_point(text: str) -> str:
    text = re.sub(r"\.{2,}", ".", text.strip())
    return re.sub(r"\s+", " ", text).strip()


class RagChatAgent(BaseAgent):
    agent_name = "rag_chat"

    def run(self, question: str, dataset_id: str | None) -> RagAnswer:
        if not dataset_id:
            return RagAnswer(
                answer="Select a dataset first so I can ground my answer in its actual data.",
                citations=[],
                retrieved_chunks=[],
            )

        context = retrieve_context(question, dataset_id, top_k=5)

        if not context.chunks:
            answer = self.narrate(
                f"Answer the analyst's question as best you can: '{question}'. "
                "No indexed context is available yet, so say so plainly and suggest "
                "uploading/processing a dataset first.",
                ["No retrieved context is available for this dataset yet"],
            )
            return RagAnswer(answer=answer, citations=[], retrieved_chunks=[])

        facts = [c.text for c in context.chunks]

        if isinstance(self._runtime, LocalDeterministicRuntime):
            # No LLM configured — narrate() only paraphrases facts and drops
            # the question, so build a direct, scannable bullet list from
            # the retrieved facts instead of a generic-feeling summary.
            points = [_clean_point(f) for f in facts]
            answer = f'On "{question.strip()}":\n' + "\n".join(f"- {p}" for p in points)
        else:
            # A real LLM is available — let it actually reason over the
            # facts and answer directly, rather than just paraphrasing them.
            answer = self.narrate(
                f"Answer the analyst's question directly and concisely, using ONLY "
                f"the retrieved facts below. Question: '{question}'. "
                "Respond as a short list of specific points (not a narrative summary) "
                "— each point should state a concrete number, name, or finding relevant "
                "to the question. If the facts don't contain the answer, say so plainly "
                "instead of guessing.",
                facts,
                dataset_id,
            )

        return RagAnswer(answer=answer, citations=context.citations, retrieved_chunks=context.chunks)
