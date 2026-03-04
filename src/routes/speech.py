from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

router = APIRouter()

_VOICES = [
    "af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky",
    "am_adam", "am_michael",
    "bf_emma", "bf_isabella",
    "bm_george", "bm_lewis",
]


class SpeechRequest(BaseModel):
    model: str = "kokoro"
    input: str
    voice: str = "af_heart"
    response_format: str = "wav"
    speed: float = 1.0
    # Extension: set stream=true to receive a chunked streaming WAV response
    stream: bool = False


@router.post("/v1/audio/speech")
async def create_speech(body: SpeechRequest, request: Request):
    engine = request.app.state.tts_engine

    if not body.input.strip():
        raise HTTPException(status_code=400, detail="input cannot be empty")

    if body.speed < 0.25 or body.speed > 4.0:
        raise HTTPException(status_code=400, detail="speed must be between 0.25 and 4.0")

    if body.stream:
        return StreamingResponse(
            engine.synthesize_streaming(body.input, body.voice, body.speed),
            media_type="audio/wav",
            headers={"X-Sample-Rate": "24000", "X-Channels": "1", "X-Bit-Depth": "16"},
        )

    audio = await engine.synthesize(body.input, body.voice, body.speed)
    return Response(
        content=audio,
        media_type="audio/wav",
        headers={"Content-Disposition": 'attachment; filename="speech.wav"'},
    )


@router.get("/v1/audio/voices")
async def list_voices():
    """Non-standard helper: list available Kokoro voice IDs."""
    return {"voices": _VOICES}
