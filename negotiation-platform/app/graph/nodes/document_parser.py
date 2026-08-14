import logging
from app.graph.state import NegotiationState
from app.agents.prompts.document_parser import DOCUMENT_PARSER_SYSTEM_PROMPT
from app.tools.openai_client import analyze_document_with_vision
from app.schemas.core import ParsedDocumentSchema

logger = logging.getLogger(__name__)

async def document_parser_node(state: NegotiationState):
    logger.info("Executing document_parser_node")
    
    # In a real scenario, state might contain raw image URLs or file contents.
    # We will simulate a document to parse if one isn't present for testing.
    
    parsed_docs = []
    
    # For testing, we mock an image URL
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Invoice_template.pdf/page1-800px-Invoice_template.pdf.jpg"
    
    try:
        parsed_doc = await analyze_document_with_vision(
            system_prompt=DOCUMENT_PARSER_SYSTEM_PROMPT,
            image_url=test_image_url,
            response_format=ParsedDocumentSchema
        )
        parsed_doc.filename = "test_invoice.jpg"
        parsed_docs.append(parsed_doc)
        
        return {
            "status": "discovering",
            "parsed_documents": parsed_docs
        }
    except Exception as e:
        logger.error(f"Document parser node failed: {e}")
        return {
            "status": "failed",
            "errors": [{"node": "document_parser", "error": str(e)}]
        }
