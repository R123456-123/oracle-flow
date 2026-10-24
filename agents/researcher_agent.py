from __future__ import annotations

from agents.shared import build_research_context, log_agent_execution


@log_agent_execution("researcher_agent")
async def researcher_agent(property_data: dict) -> dict:
	"""Build lightweight context and safety signals before the LLM calls."""
	return build_research_context(property_data)
