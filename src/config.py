from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Model paths (defaults are container paths baked at build time)
    stt_model_path: str = "/app/models/whisper"
    tts_model_dir: str = "/app/models/kokoro"
    embedding_model: str = "/app/models/nomic-moe.gguf"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Concurrency limits (semaphore per engine)
    stt_concurrency: int = 2
    tts_concurrency: int = 3
    embedding_concurrency: int = 4

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
