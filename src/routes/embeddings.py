from typing import Union

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class EmbeddingRequest(BaseModel):
    model: str = "nomic-embed-text-v2-moe"
    input: Union[str, list[str]]
    encoding_format: str = "float"
    # Extension: nomic-style prefix handling.
    # "document" → "search_document: " prefix  |  "query" → "search_query: " prefix
    input_type: str = "document"


class EmbeddingObject(BaseModel):
    object: str = "embedding"
    embedding: list[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: list[EmbeddingObject]
    model: str
    usage: dict


@router.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(body: EmbeddingRequest, request: Request):
    engine = request.app.state.embedding_engine

    texts = [body.input] if isinstance(body.input, str) else body.input
    is_query = body.input_type == "query"

    data: list[EmbeddingObject] = []
    for i, text in enumerate(texts):
        if not text.strip():
            raise HTTPException(status_code=400, detail=f"input[{i}] is empty")
        embedding = await engine.embed(text, is_query=is_query)
        data.append(EmbeddingObject(embedding=embedding, index=i))

    total_chars = sum(len(t) for t in texts)
    estimated_tokens = total_chars // 4

    return EmbeddingResponse(
        data=data,
        model=body.model,
        usage={"prompt_tokens": estimated_tokens, "total_tokens": estimated_tokens},
    )
