import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.gcs import upload_file, generate_signed_url, LOCAL_STORAGE_DIR

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload-quote")
async def upload_quote(
    negotiation_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        file_extension = Path(file.filename).suffix or ".pdf"
        dest_path = f"quotes/{negotiation_id}/{uuid.uuid4()}{file_extension}"
        
        result = upload_file(content, dest_path, content_type=file.content_type or "application/pdf")
        return {
            "negotiation_id": negotiation_id,
            "filename": file.filename,
            "result": result
        }
    except Exception as e:
        logger.error(f"Quote upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-recording")
async def upload_recording(
    negotiation_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        file_extension = Path(file.filename).suffix or ".mp3"
        dest_path = f"recordings/{negotiation_id}/{uuid.uuid4()}{file_extension}"
        
        result = upload_file(content, dest_path, content_type=file.content_type or "audio/mpeg")
        return {
            "negotiation_id": negotiation_id,
            "filename": file.filename,
            "result": result
        }
    except Exception as e:
        logger.error(f"Recording upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signed-url")
async def get_file_signed_url(file_path: str):
    try:
        url = generate_signed_url(file_path)
        return {"file_path": file_path, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_path:path}")
async def download_local_file(file_path: str):
    target = LOCAL_STORAGE_DIR / file_path
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)
