from __future__ import annotations

import functools
import json
import logging
import re
import time
from typing import Any, Callable, TypeVar

from dotenv import load_dotenv
from google import genai

from config import GEMINI_API_KEY, LLM_MODEL_ID

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_ID = LLM_MODEL_ID

INJECTION_PATTERNS = (
	"ignore previous instructions",
	"ignore the previous instructions",
	"forget previous instructions",
	"override instructions",
	"system override",
	"new persona",
	"developer mode",
	"act as",
)

OOD_PATTERNS = (
	"spaceship",
	"time machine",
	"moon base",
	"lunar",
	"mars base",
	"alien",
	"space station",
	"submarine",
)

F = TypeVar("F", bound=Callable[..., Any])


def get_client() -> genai.Client:
	if not GEMINI_API_KEY:
		raise RuntimeError("GEMINI_API_KEY is not configured")
	return genai.Client(api_key=GEMINI_API_KEY)


def normalize_text(value: Any) -> str:
	return str(value or "").strip().lower()


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
	normalized_text = normalize_text(text)
	return any(pattern in normalized_text for pattern in patterns)


def build_research_context(property_data: dict) -> dict:
	address = normalize_text(property_data.get("address"))
	property_type = normalize_text(property_data.get("property_type"))
	user_note = normalize_text(property_data.get("user_note"))
	combined_text = " ".join([address, property_type, user_note])

	prompt_injection_detected = contains_any(combined_text, INJECTION_PATTERNS)
	out_of_distribution_detected = contains_any(combined_text, OOD_PATTERNS)
	has_legal_disputes = bool(property_data.get("has_legal_disputes", False))
	size_sqft = float(property_data.get("size_sqft", 0) or 0)
	age_years = int(property_data.get("age_years", 0) or 0)

	risk_flags: list[str] = []
	if prompt_injection_detected:
		risk_flags.append("prompt_injection_signal")
	if out_of_distribution_detected:
		risk_flags.append("out_of_distribution_asset")
	if has_legal_disputes:
		risk_flags.append("reported_legal_dispute")
	if size_sqft < 100:
		risk_flags.append("very_small_asset")
	if age_years > 60:
		risk_flags.append("aged_asset")

	if any(token in property_type for token in ("apartment", "villa", "house", "residential")):
		property_class = "residential"
	elif any(token in property_type for token in ("office", "warehouse", "commercial", "retail")):
		property_class = "commercial"
	elif any(token in property_type for token in ("industrial", "factory", "plant")):
		property_class = "industrial"
	else:
		property_class = "unknown"

	verified_drivers = ["size_sqft", "age_years", "property_type", "address"]
	if has_legal_disputes:
		verified_drivers.append("has_legal_disputes")

	recommended_action = "refuse" if prompt_injection_detected or out_of_distribution_detected else "proceed"

	summary = (
		"Risk signals detected; route to refusal path."
		if recommended_action == "refuse"
		else "Property appears within the expected phase-1 operating range."
	)

	return {
		"normalized_address": address,
		"normalized_property_type": property_type,
		"property_class": property_class,
		"prompt_injection_detected": prompt_injection_detected,
		"out_of_distribution_detected": out_of_distribution_detected,
		"risk_flags": risk_flags,
		"verified_drivers": verified_drivers,
		"recommended_action": recommended_action,
		"summary": summary,
	}


def log_agent_execution(agent_name: str):
	def decorator(func: F) -> F:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			started_at = time.perf_counter()
			logger.info("%s started", agent_name)
			result = await func(*args, **kwargs)
			elapsed_seconds = time.perf_counter() - started_at
			logger.info("%s completed in %.2fs", agent_name, elapsed_seconds)
			return result

		return wrapper  # type: ignore[return-value]

	return decorator


def build_refusal_response(reason: str, research_context: dict) -> dict:
	flagged_risks = list(dict.fromkeys(research_context.get("risk_flags", []) + [reason]))

	return {
		"is_safe_to_process": False,
		"refusal_reason": reason,
		"market_value_range": [0, 0],
		"distress_value_range": [0, 0],
		"resale_potential_index": 0,
		"estimated_time_to_sell_days": [0, 0],
		"agent_confidence_score": 0.0,
		"oversight_audit_log": {
			"verified_drivers": research_context.get("verified_drivers", []),
			"flagged_risks": flagged_risks,
			"hallucination_check": "failed",
			"prompt_injection_detected": bool(research_context.get("prompt_injection_detected", False)),
			"bias_or_unsubstantiated_premium_flagged": False,
		},
	}


def build_json_prompt(title: str, property_data: dict, research_context: dict | None = None, extra_text: str = "") -> str:
	payload = json.dumps(property_data, indent=2)
	research_block = json.dumps(research_context or {}, indent=2)
	return f"""
{title}

Property data:
{payload}

Research context:
{research_block}

{extra_text}
""".strip()
