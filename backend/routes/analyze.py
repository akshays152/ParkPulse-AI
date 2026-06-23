from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import traceback

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ai.main import analyze_video

router = APIRouter(tags=["AI"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        video_path = UPLOAD_DIR / file.filename

        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = analyze_video(str(video_path))

        return JSONResponse(result)

    except Exception as e:
        traceback.print_exc()   # prints full traceback in terminal
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__
            }
        )