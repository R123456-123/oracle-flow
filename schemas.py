from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class PropertyInput(BaseModel):
    address: str = Field(..., min_length=3, description="Property address")
    property_type: str = Field(..., min_length=3, description="Type of property")
    size_sqft: float = Field(..., gt=0, description="Size in square feet")
    age_years: int = Field(..., ge=0, description="Age in years")
    has_legal_disputes: bool = Field(False, description="Known legal disputes?")

    @field_validator("address", "property_type")
    @classmethod
    def validate_no_injection(cls, v: str) -> str:
        """Basic injection detection at the API boundary."""
        injection_keywords = ["IGNORE", "OVERRIDE", "SYSTEM", "FORGET"]
        if any(keyword in v.upper() for keyword in injection_keywords):
            raise ValueError("Potential prompt injection detected in input")
        return v

    @field_validator("size_sqft")
    @classmethod
    def validate_reasonable_size(cls, v: float) -> float:
        """Reject absurd property sizes."""
        if v < 10:
            raise ValueError("Property size must be at least 10 sqft")
        if v > 10_000_000:
            raise ValueError("Property size cannot exceed 10 million sqft")
        return v


class AuditLog(BaseModel):
    verified_drivers: List[str]
    flagged_risks: List[str]
    hallucination_check: str = Field(description="Must be exactly 'passed' or 'failed'")
    prompt_injection_detected: bool = Field(description="True if the input contained manipulative instructions")
    bias_or_unsubstantiated_premium_flagged: bool = Field(description="True if the valuation relied on subjective bias rather than hard data")


class FinalValuation(BaseModel):
    is_safe_to_process: bool = Field(description="False if input is malicious, absurd, or Out-of-Distribution")
    refusal_reason: Optional[str] = Field(description="If is_safe_to_process is False, explain why. Otherwise, output 'None'")
    market_value_range: List[int] = Field(description="List of exactly two integers: [min_value, max_value]")
    distress_value_range: List[int] = Field(description="List of exactly two integers: [min_value, max_value]")
    resale_potential_index: int = Field(description="An integer representing the index from 0 to 100")
    estimated_time_to_sell_days: List[int] = Field(description="List of exactly two integers: [min_days, max_days]")
    agent_confidence_score: float = Field(description="A float representing confidence from 0.0 to 1.0")
    oversight_audit_log: AuditLog