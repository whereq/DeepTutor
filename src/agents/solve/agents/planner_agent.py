"""
PlannerAgent — Decomposes the user question into ordered solving steps.

Called once at the start (Phase 1) and optionally on replan requests.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent

from ..memory.scratchpad import Plan, PlanStep, Scratchpad
from ..utils.json_utils import extract_json_from_text

# Tools description injected into the prompt
TOOLS_DESCRIPTION = """\
- rag_search: Search the uploaded knowledge base (textbooks, lecture notes, etc.)
- web_search: Search the internet for external information
- code_execute: Execute Python code in a sandbox (calculations, plotting, data processing)"""


class PlannerAgent(BaseAgent):
    """Generates a high-level solving plan from the user question."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        api_version: str | None = None,
        token_tracker: Any | None = None,
        language: str = "en",
    ) -> None:
        super().__init__(
            module_name="solve",
            agent_name="planner_agent",
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            config=config or {},
            token_tracker=token_tracker,
            language=language,
        )

    async def process(
        self,
        question: str,
        scratchpad: Scratchpad,
        kb_name: str = "",
        replan: bool = False,
    ) -> Plan:
        """Generate or revise the solving plan.

        Args:
            question: The user's original question.
            scratchpad: Current scratchpad state.
            kb_name: Knowledge base name (informational).
            replan: If True, this is a replan request — include progress so far.

        Returns:
            A Plan object with ordered steps.
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question, scratchpad, kb_name, replan)

        response = await self.call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"},
            stage="plan" if not replan else "replan",
        )

        return self._parse_plan(response, scratchpad if replan else None)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        prompt = self.get_prompt("system") if self.has_prompts() else None
        if prompt:
            return prompt
        # Fallback if prompt file is missing
        return (
            "You are a problem-solving planner. Analyze the user's question and "
            "decompose it into ordered steps. Each step should be a verifiable sub-goal "
            "describing WHAT to establish, not HOW. Do not specify tools. "
            "Simple questions need only 1 step; complex ones may need 3-6 steps. "
            "Output strict JSON: {\"analysis\": \"...\", \"steps\": [{\"id\": \"S1\", "
            "\"goal\": \"...\"}]}"
        )

    def _build_user_prompt(
        self,
        question: str,
        scratchpad: Scratchpad,
        kb_name: str,
        replan: bool,
    ) -> str:
        template = self.get_prompt("user_template") if self.has_prompts() else None

        # Build scratchpad summary for replan
        scratchpad_summary = "(initial plan — no progress yet)"
        if replan and scratchpad.plan:
            parts: list[str] = []
            for step in scratchpad.plan.steps:
                entries = scratchpad.get_entries_for_step(step.id)
                notes = " | ".join(e.self_note for e in entries if e.self_note)
                status_label = step.status.upper()
                parts.append(f"[{step.id}] ({status_label}) {step.goal}")
                if notes:
                    parts.append(f"    Notes: {notes}")
            # Include the replan reason from the last entry
            if scratchpad.entries:
                last = scratchpad.entries[-1]
                if last.action == "replan" and last.action_input:
                    parts.append(f"\nReplan reason: {last.action_input}")
            scratchpad_summary = "\n".join(parts)

        tools_desc = TOOLS_DESCRIPTION
        if kb_name:
            tools_desc = tools_desc.replace(
                "the uploaded knowledge base",
                f'the knowledge base "{kb_name}"',
            )

        if template:
            return template.format(
                question=question,
                tools_description=tools_desc,
                scratchpad_summary=scratchpad_summary,
            )

        # Fallback
        return (
            f"## Question\n{question}\n\n"
            f"## Available Tools\n{tools_desc}\n\n"
            f"## Progress So Far\n{scratchpad_summary}"
        )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_plan(self, response: str, old_scratchpad: Scratchpad | None) -> Plan:
        """Parse LLM JSON response into a Plan object."""
        data = extract_json_from_text(response)
        if not data or not isinstance(data, dict):
            # Graceful fallback: single-step plan
            return Plan(
                analysis="Failed to parse plan; using single-step fallback.",
                steps=[PlanStep(id="S1", goal="Answer the question directly")],
            )

        analysis = data.get("analysis", "")
        raw_steps = data.get("steps", [])

        steps: list[PlanStep] = []
        for i, s in enumerate(raw_steps):
            step_id = s.get("id", f"S{i + 1}")
            goal = s.get("goal", "")
            tools_hint = s.get("tools_hint", [])
            if isinstance(tools_hint, str):
                tools_hint = [tools_hint]
            steps.append(PlanStep(id=step_id, goal=goal, tools_hint=tools_hint))

        if not steps:
            steps = [PlanStep(id="S1", goal="Answer the question")]

        return Plan(analysis=analysis, steps=steps)
