from typing import Literal, Annotated, TypedDict
import operator
from uuid import UUID
from app.schemas.core import (
    RequirementSchema,
    ParsedDocumentSchema,
    BusinessSchema,
    CallPlanSchema,
    CallRecordSchema,
    QuoteSchema,
    ComparisonMatrixSchema,
    RecommendationSchema,
    AgentErrorSchema
)

def reduce_list(left: list | None, right: list | None) -> list:
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right

class NegotiationState(TypedDict, total=False):
    negotiation_id: UUID
    status: Literal["intake", "discovering", "planning", "calling",
                     "negotiating", "analyzing", "recommending", "reporting", "done", "failed"]
    requirement: RequirementSchema | None
    parsed_documents: Annotated[list[ParsedDocumentSchema], reduce_list]
    candidate_businesses: Annotated[list[BusinessSchema], reduce_list]
    call_plan: CallPlanSchema | None
    calls: Annotated[list[CallRecordSchema], reduce_list]
    quotes: Annotated[list[QuoteSchema], reduce_list]
    quote_comparison: ComparisonMatrixSchema | None
    recommendation: RecommendationSchema | None
    report_url: str | None
    errors: Annotated[list[AgentErrorSchema], reduce_list]
    retry_counts: dict[str, int]
    requires_human_approval: bool
    checkpoint_id: str | None
