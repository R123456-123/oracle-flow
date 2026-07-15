# Oracle Flow Phase 1

## Objective

Build a production-minded foundation for Oracle Flow that is strong enough to show in a resume, useful enough to demo end-to-end, and clean enough to hand over to a team or a future phase. Phase 1 is not about perfect AI safety or a complex agent ecosystem. It is about shipping a reliable first version with solid engineering, a simple UI, and a clearly structured backend.

## Phase 1 Outcomes

By the end of this phase, the project should have:

- A working FastAPI backend with a clean request and response contract.
- A small agent system with clear separation of responsibility.
- Basic AI safety and alignment checks at the input and orchestration level.
- A simple, light, professional UI for property evaluation.
- Repeatable test runs for normal and adversarial inputs.
- A codebase organized like a real product, not a prototype.
- Resume-ready engineering outcomes that show architecture, validation, safety, and product thinking.

## Recommended Phase 1 Scope

### Backend

- Keep the API as the source of truth.
- Keep the property schema strict and stable.
- Keep the multi-agent flow small and understandable.
- Add retry handling for transient LLM failures.
- Use async end-to-end where possible.
- Add clean error handling and predictable refusal behavior.

### Frontend

- Build a simple form-first UI.
- Show evaluation status, results, and refusal reasons clearly.
- Keep the design clean, light, and easy to navigate.
- Avoid overbuilding dashboards or unnecessary animations.
- Focus on usability and clear feedback.

### AI Safety in Phase 1

- Handle prompt injection detection at a basic level.
- Reject out-of-distribution or absurd property inputs.
- Avoid subjective valuation language.
- Return structured refusal responses when needed.
- Log safety decisions in the response.

### Testing

- Validate one happy-path property.
- Validate adversarial prompt injection.
- Validate out-of-distribution cases.
- Validate legal-risk cases.
- Validate that the UI can submit and display results.

## What Good Engineering Looks Like Here

Phase 1 should demonstrate these qualities:

1. Clear ownership of each layer.
   - UI handles input and display only.
   - API handles validation and orchestration.
   - Agents handle reasoning and safety decisions.

2. Stable contracts.
   - Input and output models should not drift casually.
   - Each response should be predictable and typed.

3. Defensive LLM integration.
   - Use retries only for transient failures.
   - Do not retry bad input or schema failures.
   - Keep prompts short, direct, and role-specific.

4. Practical observability.
   - Capture evaluation state.
   - Make refusal reasons readable.
   - Make errors actionable.

5. Product-oriented UI.
   - The user should understand what was evaluated and why.
   - The result should not feel like raw debug output.

## Current Issues To Fix First

These are the main places where the current codebase is weak or inconsistent:

- The frontend currently points to `http://127.0.0.1:10000/api/v1/evaluate`, while the backend run note suggests `uvicorn main:app --reload` with no matching port defined. That needs one source of truth.
- `agents.py` currently mixes client setup, orchestration, and agent behavior in one file. This should be split into a package.
- `run_orchestration` is treated as synchronous in some places, but the actor agent is async. The call chain should be consistent.
- Retry behavior is not yet centralized. A decorator-based `retry_with_backoff` helper is the right pattern for transient model failures.
- The frontend is functional as a prototype, but the UI still reads like a demo rather than a production product.
- Safety checks exist conceptually, but they should be made more explicit, testable, and predictable.
- Error handling currently leaks generic exceptions too directly.

## Recommended Phase 1 Architecture

### Backend Package Structure

Use an `agents/` package instead of a single monolithic file.

- `agents/__init__.py`
- `agents/actor_agent.py`
- `agents/evaluator_agent.py`
- `agents/researcher_agent.py`
- `agents/shared.py`
- `agents/retry.py`

### Responsibility Split

- `actor_agent.py`: draft valuation and initial safety-aware reasoning.
- `evaluator_agent.py`: verify output, enforce schema, and return final structured response.
- `researcher_agent.py`: optional phase-1 helper only if it adds real value, such as lightweight property or market context enrichment.
- `shared.py`: client creation, model config, prompt templates, and shared helpers.
- `retry.py`: `retry_with_backoff` decorator for transient failures only.

## Recommended Retry Policy

Use retries only for:

- Rate limits.
- Temporary network errors.
- Timeouts.
- Service unavailable responses.

Do not retry:

- Invalid payloads.
- Schema validation failures.
- Safety refusals.
- Out-of-distribution properties.

This is the standard engineering approach because it avoids hiding real bugs behind automatic retries.

## UI Direction For Phase 1

Keep the UI simple and market-relevant:

- Clean form for property input.
- Clear result cards for market range, distress range, and confidence.
- Safety status visible at a glance.
- Minimal but polished visual language.
- No heavy enterprise dashboard clutter.
- No fake complexity just for visual effect.

## Resume-Ready Outcomes

Phase 1 should let you say you built:

- A multi-agent AI valuation workflow.
- A typed FastAPI service with strict input/output contracts.
- A retry-safe LLM integration layer.
- A lightweight evaluation UI.
- A safety-aware orchestration pipeline.
- A testable foundation for production AI systems.

## Phase 1 Definition Of Done

Phase 1 is complete when all of the following are true:

- The backend starts reliably.
- The frontend can submit a property and render the response.
- The agent logic is split into clear modules.
- Retry logic exists and is reusable.
- Safety checks are present and visible in the response.
- Adversarial test cases produce stable refusal behavior.
- The codebase looks like a real product foundation, not a notebook export.

## Phase 2 Handoff

Phase 2 should be reserved for deeper AI safety, richer researcher workflows, improved market intelligence, stronger monitoring, persistence, auth, and production scaling.

Phase 1 should stop at a solid, shippable, resume-worthy base.
