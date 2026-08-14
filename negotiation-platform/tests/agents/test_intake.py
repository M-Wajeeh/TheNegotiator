import pytest
from app.schemas.core import RequirementSchema
from app.agents.prompts.intake import INTAKE_SYSTEM_PROMPT
from app.tools.openai_client import generate_structured_output

@pytest.mark.asyncio
@pytest.mark.vcr
async def test_incomplete_requirement():
    user_input = "I need some help moving a couch."
    
    requirement = await generate_structured_output(
        system_prompt=INTAKE_SYSTEM_PROMPT,
        user_prompt=user_input,
        response_format=RequirementSchema
    )
    
    assert requirement.is_complete is False
    assert requirement.follow_up_question is not None
    assert len(requirement.follow_up_question) > 0

@pytest.mark.asyncio
@pytest.mark.vcr
async def test_complete_requirement():
    user_input = "I need a moving company to help me move from an apartment in downtown NYC to a house in Brooklyn. I have a 2 bedroom apartment. I need the move to happen next week."
    
    requirement = await generate_structured_output(
        system_prompt=INTAKE_SYSTEM_PROMPT,
        user_prompt=user_input,
        response_format=RequirementSchema
    )
    
    assert requirement.is_complete is True
    assert requirement.service_type is not None
    assert requirement.location is not None
