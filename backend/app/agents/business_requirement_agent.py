"""
On-demand counterpart to DecisionSupportAgent: instead of turning fixed
pipeline signals (trend/correlation/anomaly/prediction) into recommendations
automatically, this agent takes a user-stated free-text business goal and
asks the LLM to invent a tailored set of DecisionCards grounded in the
dataset's already-indexed RAG context. Kept as a sibling rather than an
extension of DecisionSupportAgent since the trigger, grounding source, and
output contract (LLM invents structure) are all different.
"""

from __future__ import annotations
import json
import re
from app.agents.base_agent import BaseAgent
from app.agentcore.runtime_client import LocalDeterministicRuntime
from app.agentcore.action_groups.rag_actions import retrieve_context
from app.models.dataset import Dataset
from app.models.decision import DecisionCard, DecisionArea, DecisionPriority
from app.models.requirement import RequirementRun, RequirementParseMode
from app.repositories.requirement_repository import requirement_repository
from app.config.logging_config import get_logger

logger = get_logger(__name__)

_VALID_AREAS = {a.value for a in DecisionArea}
_VALID_PRIORITIES = {p.value for p in DecisionPriority}

_GENERIC_ACTION_STEPS = [
    "Review this recommendation with the relevant team",
    "Validate the finding against the dataset before committing resources",
    "Decide on an owner and timeline for the next step",
]


class BusinessRequirementAgent(BaseAgent):
    agent_name = "business_requirement"

    def run(self, dataset: Dataset, requirement: str) -> RequirementRun:
        context = retrieve_context(requirement, dataset.id, top_k=8)

        if isinstance(self._runtime, LocalDeterministicRuntime):
            run = RequirementRun(
                dataset_id=dataset.id,
                requirement=requirement,
                decisions=[self._degraded_card(dataset, requirement, context)],
                parse_mode=RequirementParseMode.DEGRADED_NO_LLM,
            )
            return requirement_repository.save(run)

        instruction = self._build_instruction(dataset, requirement, context)
        raw = self.narrate(instruction, [], dataset.id, max_tokens=2000)
        cards, parse_mode = self._parse_cards(raw, dataset, requirement)

        run = RequirementRun(
            dataset_id=dataset.id,
            requirement=requirement,
            decisions=cards,
            parse_mode=parse_mode,
        )
        return requirement_repository.save(run)

    @staticmethod
    def _build_instruction(dataset: Dataset, requirement: str, context) -> str:
        return (
            "You are a business decision analyst. A user has stated this business "
            f'goal for dataset "{dataset.name}" ({dataset.row_count} rows, '
            f"{dataset.column_count} columns):\n\n"
            f'GOAL: "{requirement}"\n\n'
            "Base every recommendation strictly on the ANALYTICS CONTEXT below — "
            "do not invent numbers that aren't present there. If the context doesn't "
            "fully cover the goal, say so within a card's narrative rather than "
            "fabricating specifics.\n\n"
            f"ANALYTICS CONTEXT:\n{context.as_prompt_context()}\n\n"
            "Return ONLY a JSON array (no markdown fences, no prose before or after) "
            "of 3 to 5 objects, each with exactly these fields: "
            'title (string), area (one of: revenue, cost, customer, operations, '
            "marketing, risk), priority (one of: critical, high, medium, low), "
            "narrative (2-3 sentences), confidence (0.0-1.0), expectedRoiPct (number), "
            "impact (integer 1-5), effort (integer 1-5), estimatedValue (number), "
            "actionSteps (array of exactly 3 short strings)."
        )

    def _parse_cards(
        self, raw: str, dataset: Dataset, requirement: str
    ) -> tuple[list[DecisionCard], RequirementParseMode]:
        items = self._extract_json_list(raw)

        cards: list[DecisionCard] = []
        for item in items:
            card = self._coerce_card(item, dataset.id)
            if card:
                cards.append(card)

        if cards:
            return cards, RequirementParseMode.STRUCTURED

        logger.warning("BusinessRequirementAgent: falling back to single card for dataset %s", dataset.id)
        return [self._fallback_card(dataset, requirement, raw)], RequirementParseMode.FALLBACK_SINGLE_CARD

    @staticmethod
    def _extract_json_list(raw: str) -> list:
        text = raw.strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())

        def _try_parse(candidate: str):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                return None
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                for key in ("recommendations", "cards", "decisions"):
                    if isinstance(parsed.get(key), list):
                        return parsed[key]
            return None

        parsed = _try_parse(text)
        if parsed is not None:
            return parsed

        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            parsed = _try_parse(match.group(0))
            if parsed is not None:
                return parsed

        return []

    @staticmethod
    def _coerce_card(item: dict, dataset_id: str) -> DecisionCard | None:
        if not isinstance(item, dict):
            return None
        try:
            area = str(item.get("area", "")).strip().lower()
            area = area if area in _VALID_AREAS else DecisionArea.REVENUE.value

            priority = str(item.get("priority", "")).strip().lower()
            priority = priority if priority in _VALID_PRIORITIES else DecisionPriority.MEDIUM.value

            confidence = _clamp(_to_float(item.get("confidence"), 0.5), 0.0, 1.0)
            impact = int(_clamp(_to_float(item.get("impact"), 3), 1, 5))
            effort = int(_clamp(_to_float(item.get("effort"), 3), 1, 5))

            action_steps = item.get("actionSteps") or item.get("action_steps") or []
            if not isinstance(action_steps, list) or not action_steps:
                action_steps = list(_GENERIC_ACTION_STEPS)

            return DecisionCard(
                dataset_id=dataset_id,
                title=str(item.get("title") or "Recommendation").strip()[:200],
                area=area,
                priority=priority,
                narrative=str(item.get("narrative") or "").strip() or "No narrative provided.",
                confidence=confidence,
                expected_roi_pct=_to_float(item.get("expectedRoiPct"), 0.0),
                impact=impact,
                effort=effort,
                estimated_value=_to_float(item.get("estimatedValue"), 0.0),
                action_steps=[str(s) for s in action_steps][:3],
            )
        except Exception as exc:  # pragma: no cover - defensive against malformed LLM output
            logger.warning("Skipping malformed recommendation item: %s", exc)
            return None

    @staticmethod
    def _fallback_card(dataset: Dataset, requirement: str, raw: str) -> DecisionCard:
        lowered = requirement.lower()
        if any(k in lowered for k in ("churn", "customer", "retention")):
            area = DecisionArea.CUSTOMER.value
        elif any(k in lowered for k in ("revenue", "sales", "growth")):
            area = DecisionArea.REVENUE.value
        elif any(k in lowered for k in ("cost", "spend", "budget")):
            area = DecisionArea.COST.value
        else:
            area = DecisionArea.OPERATIONS.value

        return DecisionCard(
            dataset_id=dataset.id,
            title=f"Recommendation for: {requirement[:80]}",
            area=area,
            priority=DecisionPriority.MEDIUM.value,
            narrative=raw.strip()[:600] or "The assistant could not produce a structured recommendation.",
            confidence=0.4,
            expected_roi_pct=0.0,
            impact=3,
            effort=3,
            estimated_value=0.0,
            action_steps=list(_GENERIC_ACTION_STEPS),
        )

    @staticmethod
    def _degraded_card(dataset: Dataset, requirement: str, context) -> DecisionCard:
        narrative = (
            "A connected LLM is needed to generate tailored recommendations for this goal. "
        )
        if context.chunks:
            narrative += f"Closest available context: {context.chunks[0].text[:300]}"
        else:
            narrative += "No indexed context is available for this dataset yet."

        return DecisionCard(
            dataset_id=dataset.id,
            title=f"Recommendation for: {requirement[:80]}",
            area=DecisionArea.OPERATIONS.value,
            priority=DecisionPriority.LOW.value,
            narrative=narrative,
            confidence=0.0,
            expected_roi_pct=0.0,
            impact=1,
            effort=1,
            estimated_value=0.0,
            action_steps=["Connect a live LLM (BEDROCK_DIRECT_INVOKE) to enable this feature"],
        )


def _to_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
