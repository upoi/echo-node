# EchoNode — Installation & Bifrost Integration

## Overview

EchoNode provides always-on Speech-to-Text (Whisper-small), Text-to-Speech
(Kokoro-82M), and Text-to-Embedding (nomic-embed-text-v2-moe) via an
OpenAI-compatible REST API on port 8000. All inference runs locally on your
CPU — no cloud required.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/audio/transcriptions` | Transcribe an audio file (Whisper-small) |
| `POST` | `/v1/audio/speech` | Synthesise speech from text (Kokoro-82M) |
| `POST` | `/v1/embeddings` | Generate text embeddings (nomic-embed-text-v2-moe) |
| `GET`  | `/v1/audio/voices` | List available TTS voice IDs |
| `GET`  | `/health` | Service health and uptime |

---

## Linking EchoNode as a Custom Provider in Bifrost

1. Open **Family AI Gateway** (Bifrost) in your StartOS dashboard.
2. Navigate to **Providers → Add Custom Provider**.
3. Set the base URL to the internal StartOS address:
   ```
   http://echonode.embassy:8000
   ```
4. No API key is required — leave the key field blank.
5. Save. Bifrost will now route embedding and audio requests to EchoNode.

### Bifrost provider config (manual)

```yaml
custom_providers:
  - name: echonode
    base_url: http://echonode.embassy:8000
    api_key: ""
```

---

## Direct API Examples

### Transcribe audio
```bash
curl -X POST http://echonode.embassy:8000/v1/audio/transcriptions \
  -F file=@recording.wav \
  -F model=whisper-1
```

### Synthesise speech (streaming)
```bash
curl -X POST http://echonode.embassy:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "af_heart", "stream": true}' \
  --output speech.wav
```

### Generate embeddings
```bash
curl -X POST http://echonode.embassy:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "The quick brown fox", "input_type": "document"}'
```

---

## TTS Voices

| ID | Style |
|----|-------|
| `af_heart` | American female — warm (default) |
| `af_bella` | American female — expressive |
| `af_nicole` | American female — calm |
| `am_adam`  | American male — neutral |
| `am_michael` | American male — deep |
| `bf_emma`  | British female |
| `bm_george` | British male |

---

## Configuration

All settings are controlled via environment variables (set in
`docker_entrypoint.sh` or your StartOS service config):

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_MODEL_PATH` | `/app/models/whisper` | Path to faster-whisper model dir |
| `TTS_MODEL_DIR` | `/app/models/kokoro` | Path to Kokoro ONNX model dir |
| `EMBEDDING_MODEL` | `/app/models/nomic-moe.gguf` | Path to embedding GGUF file |
| `STT_CONCURRENCY` | `2` | Max simultaneous transcriptions |
| `TTS_CONCURRENCY` | `3` | Max simultaneous TTS requests |
| `EMBEDDING_CONCURRENCY` | `4` | Max simultaneous embedding requests |
| `PORT` | `8000` | Listen port |
