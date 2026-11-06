from __future__ import annotations

from typing import Any

from agents.shared import build_research_context, log_agent_execution


@log_agent_execution("researcher_agent")
async def researcher_agent(property_data: dict[str, Any]) -> dict[str, Any]:
    """Build lightweight context and safety signals before the LLM calls."""
    return build_research_context(property_data)
