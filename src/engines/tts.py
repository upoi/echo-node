import asyncio
import re
import struct
import time

import numpy as np
from kokoro_onnx import Kokoro

# Default voice — Kokoro American-female "heart" style
DEFAULT_VOICE = "af_heart"
SAMPLE_RATE = 24000


def _wav_header() -> bytes:
    """44-byte WAV header with unknown chunk sizes for streaming."""
    channels, bits = 1, 16
    byte_rate = SAMPLE_RATE * channels * bits // 8
    block_align = channels * bits // 8

    b = bytearray()
    b += b"RIFF"
    b += struct.pack("<I", 0xFFFFFFFF)  # total size — unknown
    b += b"WAVE"
    b += b"fmt "
    b += struct.pack("<I", 16)  # fmt chunk size
    b += struct.pack("<H", 1)  # PCM
    b += struct.pack("<H", channels)
    b += struct.pack("<I", SAMPLE_RATE)
    b += struct.pack("<I", byte_rate)
    b += struct.pack("<H", block_align)
    b += struct.pack("<H", bits)
    b += b"data"
    b += struct.pack("<I", 0xFFFFFFFF)  # data size — unknown
    return bytes(b)


def _to_pcm(samples: np.ndarray) -> bytes:
    return (samples * 32767).clip(-32768, 32767).astype(np.int16).tobytes()


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s.strip()]


class TTSEngine:
    def __init__(self, model_dir: str, concurrency: int = 3):
        self._sem = asyncio.Semaphore(concurrency)

        onnx_path = f"{model_dir}/kokoro-v1.0.onnx"
        voices_path = f"{model_dir}/voices.bin"  # downloaded as voices-v1.0.bin, renamed to voices.bin

        print(f"[tts] Loading Kokoro from {model_dir} ...")
        t0 = time.time()
        self._kokoro = Kokoro(onnx_path, voices_path)
        print(f"[tts] Loaded in {time.time() - t0:.1f}s")

    def _synth_sync(self, text: str, voice: str, speed: float) -> np.ndarray:
        samples, _ = self._kokoro.create(text, voice=voice, speed=speed, lang="en-us")
        return samples

    async def synthesize(
        self, text: str, voice: str = DEFAULT_VOICE, speed: float = 1.0
    ) -> bytes:
        """Full synthesis — returns a complete WAV file as bytes."""
        loop = asyncio.get_event_loop()

        pcm_chunks: list[bytes] = []
        async with self._sem:
            for sentence in _split_sentences(text) or [text]:
                samples = await loop.run_in_executor(
                    None, self._synth_sync, sentence, voice, speed
                )
                pcm_chunks.append(_to_pcm(samples))

        pcm = b"".join(pcm_chunks)

        # Build a properly sized WAV for the non-streaming path
        channels, bits = 1, 16
        byte_rate = SAMPLE_RATE * channels * bits // 8
        block_align = channels * bits // 8
        data_size = len(pcm)
        file_size = 36 + data_size

        b = bytearray()
        b += b"RIFF"
        b += struct.pack("<I", file_size)
        b += b"WAVE"
        b += b"fmt "
        b += struct.pack("<I", 16)
        b += struct.pack("<H", 1)
        b += struct.pack("<H", channels)
        b += struct.pack("<I", SAMPLE_RATE)
        b += struct.pack("<I", byte_rate)
        b += struct.pack("<H", block_align)
        b += struct.pack("<H", bits)
        b += b"data"
        b += struct.pack("<I", data_size)
        b += pcm
        return bytes(b)

    async def synthesize_streaming(
        self, text: str, voice: str = DEFAULT_VOICE, speed: float = 1.0
    ):
        """
        Async generator — yields a WAV header on the first chunk, then raw
        int16 PCM samples sentence-by-sentence as each is synthesised.
        Clients receive a single streamable WAV with unknown chunk sizes.
        """
        loop = asyncio.get_event_loop()
        yield _wav_header()

        async with self._sem:
            for sentence in _split_sentences(text) or [text]:
                samples = await loop.run_in_executor(
                    None, self._synth_sync, sentence, voice, speed
                )
                yield _to_pcm(samples)
