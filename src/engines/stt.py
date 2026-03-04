import asyncio
import os
import time

from faster_whisper import WhisperModel


class STTEngine:
    def __init__(self, model_path: str, concurrency: int = 2):
        self._sem = asyncio.Semaphore(concurrency)

        print(f"[stt] Loading Whisper from {model_path} ...")
        t0 = time.time()
        self._model = WhisperModel(
            model_path,
            device="cpu",
            compute_type="int8",
            cpu_threads=max(1, os.cpu_count() // 2),
            num_workers=1,
        )
        print(f"[stt] Loaded in {time.time() - t0:.1f}s")

    async def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        beam_size: int = 5,
    ) -> dict:
        async with self._sem:
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: self._model.transcribe(
                    audio_path,
                    language=language,
                    beam_size=beam_size,
                ),
            )
            # segments is a generator — exhaust it inside the executor context
            text = " ".join(s.text.strip() for s in segments)

        return {
            "text": text,
            "language": info.language,
            "duration": info.duration,
        }
