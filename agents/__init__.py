from agents.actor_agent import actor_agent
from agents.evaluator_agent import evaluator_agent
from agents.researcher_agent import researcher_agent


async def run_orchestration(property_data: dict) -> dict:
	"""
	Run the full phase-1 agent pipeline.

	The researcher builds lightweight safety and context signals first,
	the actor drafts the valuation, and the evaluator produces the final
	structured response.
	"""
	research_context = await researcher_agent(property_data)
	actor_draft = await actor_agent(property_data, research_context)
	return await evaluator_agent(property_data, actor_draft, research_context)


__all__ = [
	"run_orchestration",
	"actor_agent",
	"evaluator_agent",
	"researcher_agent",
]