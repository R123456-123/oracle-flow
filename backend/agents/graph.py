from __future__ import annotations

from typing import Any, TypedDict, cast

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from agents.retry import retry_with_backoff
from agents.shared import (
    MODEL_ID,
    build_json_prompt,
    build_refusal_response,
    build_research_context,
)
from config import GEMINI_API_KEY
from schemas import FinalValuation

MAX_JUDGE_ATTEMPTS = 3


class ActorDraft(BaseModel):
    """Structured valuation draft produced by the actor node."""

    reasoning: str = Field(description="Evidence-based valuation reasoning.")
    market_value_range: list[int] = Field(min_length=2, max_length=2)
    distress_value_range: list[int] = Field(min_length=2, max_length=2)
    resale_potential_index: int = Field(ge=0, le=100)
    estimated_time_to_sell_days: list[int] = Field(min_length=2, max_length=2)


class JudgeResult(BaseModel):
    """Structured evaluator result with feedback for retryable failures."""

    valuation: FinalValuation
    passed: bool = Field(description="Whether the draft passed safety and quality checks.")
    feedback: str = Field(description="Actionable feedback for a retry.")


class GraphState(TypedDict, total=False):
    """State passed between LangGraph valuation nodes."""

    property_data: dict[str, Any]
    research_context: dict[str, Any]
    actor_draft: ActorDraft
    judge_result: JudgeResult
    final_valuation: dict[str, Any]
    judge_feedback: str
    judge_attempts: int


def _create_llm() -> BaseChatModel:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return ChatGoogleGenerativeAI(
        model=MODEL_ID,
        api_key=GEMINI_API_KEY,
        temperature=0,
    )


def _structured_model(llm: BaseChatModel, schema: type[BaseModel]) -> Any:
    return llm.with_structured_output(schema, method="json_schema")


@retry_with_backoff(max_retries=3, initial_backoff=1.0, max_backoff=8.0)  # type: ignore[misc]
async def _invoke_structured(model: Any, prompt: str) -> Any:
    return await model.ainvoke(prompt)


async def guard_input(state: GraphState) -> dict[str, Any]:
    """Build the deterministic safety context before any model call."""
    context = build_research_context(state["property_data"])
    return {
        "research_context": context,
        "judge_attempts": 0,
        "judge_feedback": "",
    }


async def researcher(state: GraphState) -> dict[str, Any]:
    """Expose the researcher stage as an explicit graph node."""
    return {}


async def actor(state: GraphState, *, llm: BaseChatModel) -> dict[str, Any]:
    """Generate a structured evidence-based valuation draft."""
    context = state["research_context"]
    if context.get("recommended_action") == "refuse":
        return {}

    prompt = build_json_prompt(
        title="Draft a structured real-estate valuation.",
        property_data=state["property_data"],
        research_context=context,
        extra_text=(
            "Return only the requested structured fields. Use empirical inputs only. "
            f"Previous judge feedback: {state.get('judge_feedback', '')}"
        ),
    )
    model = _structured_model(llm, ActorDraft)
    draft = await _invoke_structured(model, prompt)
    if not isinstance(draft, ActorDraft):
        draft = ActorDraft.model_validate(draft)
    return {"actor_draft": draft}


async def judge(state: GraphState, *, llm: BaseChatModel) -> dict[str, Any]:
    """Review the actor draft and return structured output plus retry feedback."""
    context = state["research_context"]
    if context.get("recommended_action") == "refuse":
        reason = (
            "Prompt injection or out-of-distribution input detected during phase-1 safety review."
        )
        valuation = build_refusal_response(reason, context)
        return {
            "judge_result": JudgeResult(
                valuation=FinalValuation.model_validate(valuation),
                passed=False,
                feedback=reason,
            ),
            "final_valuation": valuation,
        }

    prompt = build_json_prompt(
        title="Evaluate the actor draft and return the final structured valuation.",
        property_data=state["property_data"],
        research_context=context,
        extra_text=(
            f"Actor draft:\n{state['actor_draft'].model_dump_json(indent=2)}\n"
            f"Previous judge feedback: {state.get('judge_feedback', '')}\n"
            "Reject unsafe, biased, or unsupported reasoning and zero financial values."
        ),
    )
    model = _structured_model(llm, JudgeResult)
    result = await _invoke_structured(model, prompt)
    if not isinstance(result, JudgeResult):
        result = JudgeResult.model_validate(result)
    valuation = result.valuation.model_dump()
    valuation["currency"] = state["property_data"].get("currency", "USD")
    if valuation["refusal_reason"] == "None":
        valuation["refusal_reason"] = None
    return {
        "judge_result": result,
        "judge_feedback": result.feedback,
        "judge_attempts": state.get("judge_attempts", 0) + 1,
        "final_valuation": valuation,
    }


async def finalize(state: GraphState) -> dict[str, Any]:
    """Return the final validated valuation from graph state."""
    if "final_valuation" in state:
        return cast(dict[str, Any], state)
    return {
        "final_valuation": build_refusal_response(
            "Evaluation did not produce a final result.",
            state["research_context"],
        )
    }


def _guard_route(state: GraphState) -> str:
    if state["research_context"].get("recommended_action") == "refuse":
        return "finalize"
    return "researcher"


def _judge_route(state: GraphState) -> str:
    result = state.get("judge_result")
    if result is None:
        return "finalize"
    if result.passed or state.get("judge_attempts", 0) >= MAX_JUDGE_ATTEMPTS:
        return "finalize"
    return "actor"


def build_graph(llm: BaseChatModel | None = None) -> Any:
    """Build and compile the Oracle Flow LangGraph state machine."""
    model = llm or _create_llm()
    graph = StateGraph(GraphState)

    async def actor_node(state: GraphState) -> dict[str, Any]:
        return await actor(state, llm=model)

    async def judge_node(state: GraphState) -> dict[str, Any]:
        return await judge(state, llm=model)

    graph.add_node("guard_input", guard_input)
    graph.add_node("researcher", researcher)
    graph.add_node("actor", actor_node)
    graph.add_node("judge", judge_node)
    graph.add_node("finalize", finalize)
    graph.add_edge(START, "guard_input")
    graph.add_conditional_edges(
        "guard_input",
        _guard_route,
        {"researcher": "researcher", "finalize": "finalize"},
    )
    graph.add_edge("researcher", "actor")
    graph.add_edge("actor", "judge")
    graph.add_conditional_edges("judge", _judge_route, {"actor": "actor", "finalize": "finalize"})
    graph.add_edge("finalize", END)
    return graph.compile()


async def run_graph(
    property_data: dict[str, Any], llm: BaseChatModel | None = None
) -> dict[str, Any]:
    """Run one property evaluation through the compiled graph."""
    app = build_graph(llm)
    result = await app.ainvoke({"property_data": property_data})
    return cast(dict[str, Any], result["final_valuation"])
