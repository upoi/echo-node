#!/bin/bash
set -e

mkdir -p /app/data

echo "Starting EchoNode..."
echo "  STT model : ${STT_MODEL_PATH:-/app/models/whisper}"
echo "  TTS dir   : ${TTS_MODEL_DIR:-/app/models/kokoro}"
echo "  Embed model: ${EMBEDDING_MODEL:-/app/models/nomic-moe.gguf}"

exec python -m uvicorn src.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --workers 1 \
    --log-level info
