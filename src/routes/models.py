import time
from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/models")
async def list_models():
    """Return a static list of models supported by EchoNode."""
    created = int(time.time())
    return {
        "object": "list",
        "data": [
            {
                "id": "whisper-1",
                "object": "model",
                "created": created,
                "owned_by": "echonode"
            },
            {
                "id": "kokoro",
                "object": "model",
                "created": created,
                "owned_by": "echonode"
            },
            {
                "id": "nomic-embed-text-v2-moe",
                "object": "model",
                "created": created,
                "owned_by": "echonode"
            }
        ]
    }
