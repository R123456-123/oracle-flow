from uuid import uuid4

from models import AgentStep, EvaluationRun


def test_evaluation_run_model_contains_requested_fields() -> None:
    run = EvaluationRun(
        input={"address": "123 Main Street"},
        output={"is_safe_to_process": True},
        status="completed",
        latency_ms=125,
        model="test-model",
    )

    assert run.id is None
    assert run.input["address"] == "123 Main Street"
    assert run.status == "completed"
    assert run.created_at is None


def test_agent_step_model_links_to_evaluation_run() -> None:
    run_id = uuid4()
    step = AgentStep(
        run_id=run_id,
        node="researcher",
        score=0.9,
        feedback="safe",
        tokens=12,
    )

    assert step.run_id == run_id
    assert step.node == "researcher"
    assert step.created_at is None
