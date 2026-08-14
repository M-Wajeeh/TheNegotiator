import pytest
from app.schemas.core import RequirementSchema
from app.graph.state import NegotiationState
from app.graph.nodes.business_discovery import business_discovery_node

@pytest.mark.asyncio
@pytest.mark.vcr
async def test_business_discovery_success():
    req = RequirementSchema(
        service_type="Plumbers",
        location="San Francisco, CA",
        is_complete=True
    )
    state = {"requirement": req}
    
    result = await business_discovery_node(state)
    
    assert result["status"] == "planning"
    assert len(result["candidate_businesses"]) > 0
    # Every business must have name, phone, business_id
    for biz in result["candidate_businesses"]:
        assert biz.name
        assert biz.phone
        assert biz.business_id

@pytest.mark.asyncio
async def test_business_discovery_missing_req():
    state = {}
    result = await business_discovery_node(state)
    assert result["status"] == "failed"
    assert "Missing requirement" in result["errors"][0]["error"]
