This set of instructions is designed for a coding agent to begin packaging your standalone Audio & Embedding Utility service for StartOS. The focus is on creating a robust model-serving layer that integrates seamlessly into your existing Bifrost-led architecture.
Project Goal: Standalone CPU AI Utility Service
Create a StartOS service (suggested ID: vector-vox or echonode) that provides always-available Speech-to-Text (STT), Text-to-Speech (TTS), and Text-to-Embedding capabilities via an OpenAI-compatible REST API, optimized for the Intel i7-10710U CPU.

--------------------------------------------------------------------------------
Step 1: Core Technology Stack
Primary Engine: Use sherpa-onnx as the base runtime. It is self-contained, supports everything requested (STT, TTS, and embeddings), and can be compiled from source for optimized CPU performance.
Inference Backend: Ensure the build utilizes Intel-specific optimizations (like oneMKL) to maximize the i7's throughput.
API Layer: Implement a lightweight Python FastAPI or Go wrapper to expose sherpa-onnx capabilities through standard OpenAI-compatible endpoints:
/v1/audio/transcriptions (Whisper models).
/v1/audio/speech (TTS models like Piper or Kokoro).
/v1/embeddings (Embedding models).
Step 2: StartOS Packaging Requirements
The agent must construct a standard Start9 service wrapper containing:
manifest.yaml: Define the package ID, version, and a single HTTP Interface (e.g., port 8000) for internal hub communication.
Dockerfile:
Use a lightweight base (e.g., Debian Bullseye).
Multi-stage build to compile sherpa-onnx with CPU optimizations.
Optimize image size to stay under 1GB.
docker_entrypoint.sh: Govern the startup of the API wrapper and the loading of default "always-on" models.
instructions.md: Detail how to link this service as a Custom Provider in Bifrost.
Step 3: Bifrost Integration Design
The service must be discoverable by Bifrost.
Provider Config: Bifrost will use a custom_provider_config with a base_url pointing to the service’s internal StartOS address (e.g., http://vector-vox.local:8000).
Concurrency: The service should report health status to Bifrost, allowing the gateway to manage the request buffer and prevent CPU saturation.

--------------------------------------------------------------------------------
Decisions Still Pending
Framework Choice: Should we stick with the highly integrated sherpa-onnx (lower overhead, C++ core), or build a modular Python stack using faster-whisper and Piper? faster-whisper is often preferred for high-accuracy Intel CPU transcription.
Specific Model Variants:
STT: Do we default to whisper-base for speed or whisper-small for better accuracy on the i7?.
TTS: Which model provides the best "natural" feel for the family? Kokoro is currently leading for quality-to-speed ratio on CPUs.
Embedding: Which model size? BGE-small is excellent for speed, but All-MiniLM-L6-v2 is the standard for general-purpose hub RAG.
Persistence Layer: Will the service bundle its own storage for downloaded models, or should it use a StartOS Volume to allow users to sideload their own GGUF/ONNX models?.
Concurrency Handling: How many simultaneous audio streams should we allow by default? Given the 6-core i7, a limit of 2–3 concurrent STT tasks is a safe starting point to prevent blocking other family apps.
Agent Instruction Handoff
"Agent, begin by creating the Dockerfile and manifest.yaml for a StartOS service that wraps sherpa-onnx. Ensure the build is optimized for x86_64 CPUs. Focus on exposing an OpenAI-compatible API for the /v1/embeddings and /v1/audio/transcriptions endpoints. For now, assume a 256MB RAM overhead for the 'tiny' Whisper model and provide a configuration option to toggle TTS."