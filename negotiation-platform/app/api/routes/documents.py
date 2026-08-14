from fastapi import APIRouter, UploadFile, File
router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return {"status": "document parsed", "filename": file.filename}
