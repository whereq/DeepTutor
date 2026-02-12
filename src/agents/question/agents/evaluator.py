#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Evaluator - Score idea candidates and select top-k templates.
"""

from __future__ import annotations

import json
from typing import Any

from src.agents.base_agent import BaseAgent
from src.agents.question.models import QuestionTemplate


class Evaluator(BaseAgent):
    """
    Evaluate idea quality/diversity and decide whether to continue idea loop.
    """

    def __init__(self, language: str = "en", **kwargs: Any) -> None:
        super().__init__(
            module_name="question",
            agent_name="evaluator",
            language=language,
            **kwargs,
        )

    async def process(
        self,
        user_topic: str,
        preference: str,
        ideas: list[dict[str, Any]],
        top_k: int,
        current_round: int,
        max_rounds: int,
        target_difficulty: str = "",
        target_question_type: str = "",
    ) -> dict[str, Any]:
        """
        Return either feedback (continue) or selected templates (stop).
        """
        system_prompt = self.get_prompt("system", "")
        evaluate_prompt = self.get_prompt("evaluate_ideas", "")
        if not evaluate_prompt:
            evaluate_prompt = (
                "Topic: {user_topic}\n"
                "Preference: {preference}\n"
                "Round: {current_round}/{max_rounds}\n"
                "Ideas:\n{ideas_json}\n\n"
                'Return JSON {"continue_loop": bool, "feedback": "...", "selected_ideas":[...]}'
            )

        constraints: list[str] = []
        if target_difficulty:
            constraints.append(f"Target difficulty: {target_difficulty}")
        if target_question_type:
            constraints.append(f"Target question type: {target_question_type}")
        effective_preference = preference or "(none)"
        if constraints:
            effective_preference = f"{effective_preference}\n" + "\n".join(constraints)

        user_prompt = evaluate_prompt.format(
            user_topic=user_topic,
            preference=effective_preference,
            current_round=current_round,
            max_rounds=max_rounds,
            top_k=top_k,
            ideas_json=json.dumps(ideas, ensure_ascii=False, indent=2),
        )

        parsed = await self._evaluate_with_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt or "",
            ideas=ideas,
            top_k=top_k,
        )

        continue_loop = bool(parsed.get("continue_loop", False))
        if current_round >= max_rounds:
            continue_loop = False

        selected_ideas = parsed.get("selected_ideas", [])
        if not isinstance(selected_ideas, list):
            selected_ideas = []

        # Ensure selected ideas exist
        if not selected_ideas:
            selected_ideas = self._fallback_select(ideas=ideas, top_k=top_k)

        templates = self._ideas_to_templates(selected_ideas, top_k=top_k)
        return {
            "continue_loop": continue_loop,
            "feedback": str(parsed.get("feedback", "")).strip(),
            "templates": templates,
            "selected_ideas": selected_ideas[:top_k],
            "scores": parsed.get("scores", []),
        }

    async def _evaluate_with_llm(
        self,
        user_prompt: str,
        system_prompt: str,
        ideas: list[dict[str, Any]],
        top_k: int,
    ) -> dict[str, Any]:
        try:
            response = await self.call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                temperature=0.2,
                stage="evaluate_idea_candidates",
            )
            payload = json.loads(response)
            if isinstance(payload, dict):
                return payload
        except Exception as exc:
            self.logger.warning(f"Evaluator parse failed, fallback used: {exc}")
        return {
            "continue_loop": False,
            "feedback": "",
            "selected_ideas": self._fallback_select(ideas=ideas, top_k=top_k),
            "scores": [],
        }

    def _fallback_select(self, ideas: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        valid = [idea for idea in ideas if isinstance(idea, dict) and idea.get("concentration")]
        return valid[:top_k]

    def _ideas_to_templates(
        self,
        selected_ideas: list[dict[str, Any]],
        top_k: int,
    ) -> list[QuestionTemplate]:
        templates: list[QuestionTemplate] = []
        for idx, item in enumerate(selected_ideas[:top_k], 1):
            if not isinstance(item, dict):
                continue
            concentration = str(item.get("concentration", "")).strip()
            if not concentration:
                continue
            templates.append(
                QuestionTemplate(
                    question_id=f"q_{idx}",
                    concentration=concentration,
                    question_type=str(item.get("question_type", "written")).strip() or "written",
                    difficulty=str(item.get("difficulty", "medium")).strip() or "medium",
                    source="custom",
                    metadata={
                        "idea_id": item.get("idea_id", f"idea_{idx}"),
                        "rationale": item.get("rationale", ""),
                    },
                )
            )

        # Ensure enough templates for downstream generation
        if len(templates) < top_k:
            for idx in range(len(templates) + 1, top_k + 1):
                templates.append(
                    QuestionTemplate(
                        question_id=f"q_{idx}",
                        concentration=f"Aspect {idx}",
                        question_type="written",
                        difficulty="medium",
                        source="custom",
                    )
                )
        return templates
