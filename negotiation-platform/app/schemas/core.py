from pydantic import BaseModel, Field
from typing import Any

class RequirementSchema(BaseModel):
    service_type: str | None = None
    location: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    is_complete: bool = False
    follow_up_question: str | None = None

class ParsedDocumentSchema(BaseModel):
    filename: str
    business_name: str | None = None
    total_amount: float | None = None
    extracted_details: dict[str, Any] = Field(default_factory=dict)
    raw_content: str | None = None

class BusinessSchema(BaseModel):
    business_id: str
    name: str
    phone: str
    website: str | None = None
    rating: float | None = None

class CallPlanSchema(BaseModel):
    strategy: str
    max_calls: int
    focus_areas: list[str] = Field(default_factory=list)

class CallRecordSchema(BaseModel):
    business_id: str
    call_id: str
    status: str
    outcome: str
    transcript: str | None = None

class QuoteSchema(BaseModel):
    business_id: str
    amount: float
    details: dict[str, Any] = Field(default_factory=dict)

class ComparisonMatrixSchema(BaseModel):
    comparisons: dict[str, Any] = Field(default_factory=dict)

class RecommendationSchema(BaseModel):
    recommended_business_id: str
    reasoning: str

class AgentErrorSchema(BaseModel):
    node: str
    error: str
