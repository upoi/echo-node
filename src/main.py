import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.engines.embeddings import EmbeddingEngine
from src.engines.stt import STTEngine
from src.engines.tts import TTSEngine
from src.routes import embeddings, models, speech, transcriptions

_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embedding_engine = EmbeddingEngine(
        model_path=settings.embedding_model,
        concurrency=settings.embedding_concurrency,
    )
    app.state.stt_engine = STTEngine(
        model_path=settings.stt_model_path,
        concurrency=settings.stt_concurrency,
    )
    app.state.tts_engine = TTSEngine(
        model_dir=settings.tts_model_dir,
        concurrency=settings.tts_concurrency,
    )
    yield


app = FastAPI(title="EchoNode", version="0.1.0", lifespan=lifespan)

app.include_router(embeddings.router)
app.include_router(transcriptions.router)
app.include_router(speech.router)
app.include_router(models.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - _start_time),
        "models": {
            "stt": settings.stt_model_path,
            "tts": settings.tts_model_dir,
            "embeddings": settings.embedding_model,
        },
    }
