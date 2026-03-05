# ─── Stage 1: compile llama-cpp-python with OpenBLAS ─────────────────────────
FROM python:3.12-slim-bookworm AS llama-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libopenblas-dev pkg-config git \
    && rm -rf /var/lib/apt/lists/*

RUN CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    pip install --no-cache-dir "llama-cpp-python>=0.3.0,<0.4.0"

# ─── Stage 2: download Whisper-small and Kokoro ONNX models ──────────────────
FROM python:3.12-slim-bookworm AS model-fetcher

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir huggingface-hub faster-whisper

# Whisper small (CTranslate2 quantised INT8 format)
RUN python -c "\
from huggingface_hub import snapshot_download; \
snapshot_download('Systran/faster-whisper-small', local_dir='/models/whisper')"

# Kokoro ONNX model + voices — hexgrad/Kokoro-82M has PyTorch weights only;
# the ONNX build is published as release assets on the kokoro-onnx GitHub repo.
RUN mkdir -p /models/kokoro && \
    wget -q -O /models/kokoro/kokoro-v1.0.onnx \
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx" && \
    wget -q -O /models/kokoro/voices.bin \
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

# ─── Stage 3: final runtime image ────────────────────────────────────────────
FROM python:3.12-slim-bookworm

# Flush Python stdout/stderr immediately so StartOS logs are visible in real time
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy llama-cpp-python (compiled with BLAS) from stage 1
COPY --from=llama-builder \
    /usr/local/lib/python3.12/site-packages/llama_cpp \
    /usr/local/lib/python3.12/site-packages/llama_cpp
COPY --from=llama-builder \
    /usr/local/lib/python3.12/site-packages/llama_cpp_python-*.dist-info \
    /usr/local/lib/python3.12/site-packages/

# Install remaining Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy pre-downloaded models from stage 2
COPY --from=model-fetcher /models/whisper /app/models/whisper
COPY --from=model-fetcher /models/kokoro  /app/models/kokoro

# Bundle the quantised embedding model (must be present at build time)
COPY models/nomic-moe.gguf /app/models/nomic-moe.gguf

# Application source
COPY src/ /app/src/

WORKDIR /app

EXPOSE 8000

COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh

ENTRYPOINT ["/docker_entrypoint.sh"]
