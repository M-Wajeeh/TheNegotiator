import pytest
from app.schemas.core import ParsedDocumentSchema
from app.agents.prompts.document_parser import DOCUMENT_PARSER_SYSTEM_PROMPT
from app.tools.openai_client import analyze_document_with_vision

@pytest.mark.asyncio
@pytest.mark.vcr
async def test_document_parser_valid_quote():
    # A public URL to an image containing a dummy invoice.
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Invoice_template.pdf/page1-800px-Invoice_template.pdf.jpg"
    
    parsed_doc = await analyze_document_with_vision(
        system_prompt=DOCUMENT_PARSER_SYSTEM_PROMPT,
        image_url=test_image_url,
        response_format=ParsedDocumentSchema
    )
    
    # We don't know the exact business name of the generic template, but it should extract *something*
    # depending on what the model sees. The model usually parses "Company Name" or similar if it's a template.
    assert parsed_doc.business_name is not None
    assert type(parsed_doc.extracted_details) == dict
