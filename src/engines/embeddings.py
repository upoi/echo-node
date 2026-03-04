import asyncio
import os
import time

from llama_cpp import Llama


class EmbeddingEngine:
    def __init__(self, model_path: str, concurrency: int = 4):
        self._sem = asyncio.Semaphore(concurrency)
        self._requests = 0

        print(f"[embeddings] Loading {model_path} ...")
        t0 = time.time()
        self._llm = Llama(
            model_path=model_path,
            embedding=True,
            n_ctx=512,
            n_threads=os.cpu_count(),
            verbose=False,
        )
        print(f"[embeddings] Loaded in {time.time() - t0:.1f}s")

    async def embed(self, text: str, is_query: bool = False) -> list[float]:
        prefix = "search_query: " if is_query else "search_document: "
        full_text = f"{prefix}{text}"

        async with self._sem:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._llm.create_embedding, full_text
            )

        self._requests += 1
        return result["data"][0]["embedding"]
