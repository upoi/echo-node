import os
import tempfile
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import PlainTextResponse

router = APIRouter()

_ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".flac"}


@router.post("/v1/audio/transcriptions")
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    model: str = Form("whisper-1"),
    language: Optional[str] = Form(None),
    response_format: str = Form("json"),
):
    engine = request.app.state.stt_engine

    ext = os.path.splitext(file.filename or "audio.wav")[1].lower() or ".wav"
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = await engine.transcribe(tmp_path, language=language or None)
    finally:
        os.unlink(tmp_path)

    if response_format == "text":
        return PlainTextResponse(result["text"])

    if response_format == "verbose_json":
        return {
            "task": "transcribe",
            "language": result["language"],
            "duration": result["duration"],
            "text": result["text"],
        }

    return {"text": result["text"]}
