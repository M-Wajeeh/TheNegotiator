import logging
from pathlib import Path

logger = logging.getLogger(__name__)

LOCAL_STORAGE_DIR = Path(__file__).resolve().parents[2] / "uploads"

def upload_file(file_bytes: bytes, destination_path: str, content_type: str = "application/pdf") -> dict:
    """
    Uploads file content to local storage directory.
    """
    try:
        local_path = LOCAL_STORAGE_DIR / destination_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        
        logger.info(f"File stored locally at {local_path}")
        return {
            "status": "uploaded",
            "storage": "local",
            "path": destination_path,
            "url": f"/api/files/download/{destination_path}"
        }
    except Exception as e:
        logger.error(f"Local storage upload failed for {destination_path}: {e}")
        return {"status": "error", "error": str(e)}

def generate_signed_url(destination_path: str, expiration_minutes: int = 60) -> str:
    """
    Returns relative download URL for locally stored file.
    """
    return f"/api/files/download/{destination_path}"
