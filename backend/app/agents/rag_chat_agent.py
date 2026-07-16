from __future__ import annotations
import re
from app.agents.base_agent import BaseAgent
from app.agentcore.runtime_client import LocalDeterministicRuntime
from app.rag.schemas.rag_schema import RagAnswer, RagContext
from app.agentcore.action_groups.rag_actions import retrieve_context


def _clean_point(text: str) -> str:
    text = re.sub(r"\.{2,}", ".", text.strip())
    return re.sub(r"\s+", " ", text).strip()


class RagChatAgent(BaseAgent):
    agent_name = "rag_chat"

    def run(self, question: str, dataset_id: str | None) -> RagAnswer:
        # A dataset is optional: when one is selected we retrieve grounded
        # context and cite it, but the assistant still answers general
        # questions (or questions the retrieved facts don't cover) using
        # its own knowledge rather than refusing outright.
        context = retrieve_context(question, dataset_id, top_k=5) if dataset_id else RagContext()
        facts = [c.text for c in context.chunks]

        if isinstance(self._runtime, LocalDeterministicRuntime):
            # No LLM configured — narrate() only paraphrases facts and drops
            # the question, so build a direct, scannable bullet list from
            # the retrieved facts when there are any.
            if facts:
                points = [_clean_point(f) for f in facts]
                answer = f'On "{question.strip()}":\n' + "\n".join(f"- {p}" for p in points)
            else:
                answer = self.narrate(
                    f"Answer the analyst's question as best you can: '{question}'.",
                    ["No dataset-specific context is available for this question"],
                )
        elif facts:
            # A real LLM is available and we have grounded context — prefer
            # it, but allow falling back to general knowledge for anything
            # the facts don't cover instead of refusing.
            answer = self.narrate(
                f"Answer the analyst's question directly and concisely. Question: '{question}'. "
                "Ground your answer in the retrieved facts below whenever they're relevant. "
                "If the facts don't fully cover the question, answer using your own general "
                "knowledge instead of refusing, and make clear which parts of your answer are "
                "specific to this dataset versus general knowledge. Respond as a short list of "
                "specific points where possible.",
                facts,
                dataset_id,
            )
        else:
            # No LLM-usable context at all (no dataset selected, or nothing
            # indexed for it yet) — answer as a general-purpose assistant.
            answer = self.narrate(
                f"Answer the analyst's question directly and helpfully, using your own "
                f"general knowledge: '{question}'. No dataset-specific context is available "
                "for this question, so don't claim the answer comes from any dataset.",
                [],
                dataset_id,
            )

        return RagAnswer(answer=answer, citations=context.citations, retrieved_chunks=context.chunks)
