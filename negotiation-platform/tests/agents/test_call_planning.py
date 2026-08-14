import pytest
from app.schemas.core import RequirementSchema, BusinessSchema
from app.graph.nodes.call_planning import call_planning_node

@pytest.mark.asyncio
@pytest.mark.vcr
async def test_call_planning():
    req = RequirementSchema(
        service_type="Plumbers",
        location="San Francisco, CA",
        details={"issue": "Leaking pipe under sink"},
        is_complete=True
    )
    candidates = [
        BusinessSchema(business_id="1", name="SF Plumbers", phone="123"),
        BusinessSchema(business_id="2", name="Bay Area Plumbing", phone="456")
    ]
    
    state = {"requirement": req, "candidate_businesses": candidates}
    
    result = await call_planning_node(state)
    
    assert result["status"] == "calling"
    assert result["call_plan"] is not None
    assert result["call_plan"].strategy
    assert len(result["call_plan"].focus_areas) > 0
