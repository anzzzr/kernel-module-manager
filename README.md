# AI-Powered Linux Kernel Module Diagnostic Assistant

Go REST API + Python FastAPI microservice with **real RAG** (Retrieval-Augmented Generation) using ChromaDB and sentence-transformers, plus LLM-based diagnosis via any OpenAI-compatible API.

## Architecture

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="AI-Powered Kernel Module Manager Architecture" width="100%" />
</p>

<p align="center">
  <em>Interactive version with pan/zoom/inspect: <a href="docs/diagrams/architecture.html"><b>docs/diagrams/architecture.html</b></a> (source: <a href="docs/diagrams/architecture.json">architecture.json</a>)</em>
</p>

```
                        USER
                         │
                         ▼
                   Go REST API
                    Port 8080
                         │
            ┌────────────┼────────────┐
            │                         │
            ▼                         ▼
      Module Manager          Diagnostic Collector
      modprobe/rmmod           uname, lsmod, modinfo,
                               dmesg, journalctl,
                               modprobe --show-depends
                                         │
                                         ▼
                                  Python FastAPI
                                   Port 8001
                                         │
                           ┌─────────────┼─────────────┐
                           │                           │
                           ▼                           ▼
                     RAG Pipeline                  LLM API
                           │                     (OpenAI/Groq)
                           ▼                           │
                       ChromaDB                        │
                   sentence-transformers               │
                   Linux kernel docs                   │
                           │                           │
                           └─────────────┼─────────────┘
                                         ▼
                                  Structured JSON
                                    Diagnosis
```

### Components

**Go Backend** — REST API with token auth, module load/unload operations, diagnostic evidence collection from 7 Linux commands, and forwarding to the AI service.

**Python FastAPI Service** — Receives diagnostic evidence, retrieves relevant documentation via RAG, sends evidence + context to an LLM, validates and returns structured diagnosis.

**RAG Pipeline** — Linux kernel documentation embedded with `all-MiniLM-L6-v2`, stored in ChromaDB, retrieved via cosine similarity search to ground LLM diagnoses in real documentation.

## Quick Start

### Prerequisites

- Go 1.23+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended for Python)
- An API key for OpenAI, Groq, or any OpenAI-compatible LLM provider

### 1. Start the Python AI Service

```bash
cd ai_service
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e .

export LLM_API_KEY='your-llm-api-key'
export AI_SERVICE_TOKEN='shared-secret'
# For Groq:
# export LLM_BASE_URL='https://api.groq.com/openai/v1'
# export LLM_MODEL='llama-3.3-70b-versatile'

# Run via CLI:
kernel-ai serve --host 127.0.0.1 --port 8001
# (or via uvicorn: uvicorn kernel_diagnostic_ai.main:app --port 8001)
```

On first startup, the RAG pipeline loads documentation from `docs/`, generates embeddings, and populates ChromaDB. This takes ~10 seconds on the first run.

### 2. Start the Go Backend

```bash
# From repository root
export MODULE_API_TOKEN='your-api-token'
export AI_SERVICE_TOKEN='shared-secret'
export AI_SERVICE_URL='http://127.0.0.1:8001'

go run .
```

### 3. Diagnose a Module

```bash
curl -s -X POST http://127.0.0.1:8080/module/nvidia/diagnose \
  -H 'Authorization: Bearer your-api-token' | python3 -m json.tool
```

## API Endpoints

### Go Backend (port 8080)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/module/{module}/diagnose` | Yes | AI-powered module diagnosis |
| POST | `/module/load/{module}` | Yes | Load kernel module (privileged) |
| POST | `/module/unload/{module}` | Yes | Unload kernel module (privileged) |

### Python AI Service (port 8001)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check with RAG status |
| POST | `/analyze` | Optional | Analyze diagnostic evidence |

### Example Diagnosis Response

```json
{
  "module": "nvidia",
  "evidence": {
    "module": "nvidia",
    "commands": { "uname": "5.15.0-91-generic", "lsmod": "...", "modinfo": "..." },
    "errors": {}
  },
  "ai_analysis": {
    "diagnosis": "NVIDIA kernel module version mismatch detected",
    "possible_causes": [
      "Driver compiled for different kernel version",
      "DKMS rebuild not triggered after kernel update"
    ],
    "recommendations": [
      "Run sudo dkms autoinstall to rebuild for current kernel",
      "Verify kernel headers are installed: apt install linux-headers-$(uname -r)"
    ],
    "evidence_used": [
      "vermagic string does not match running kernel",
      "modinfo shows module built for 5.15.0-88-generic"
    ],
    "uncertainty": "low",
    "documentation_references": [
      "module_loading.md - vermagic String",
      "nvidia_troubleshooting.md - Kernel Version Mismatch"
    ]
  },
  "rag_context_used": true
}
```

## Environment Variables

See [`.env.example`](.env.example) for all configuration options.

| Variable | Service | Required | Default | Description |
|----------|---------|----------|---------|-------------|
| `MODULE_API_TOKEN` | Go | Yes | — | Auth token for Go API |
| `AI_SERVICE_URL` | Go | No | — | Python service URL |
| `AI_SERVICE_TOKEN` | Both | No | — | Shared token between services |
| `LLM_API_KEY` | Python | Yes | — | LLM provider API key |
| `LLM_BASE_URL` | Python | No | `https://api.openai.com/v1` | LLM API base URL |
| `LLM_MODEL` | Python | No | `gpt-4o-mini` | LLM model name |
| `RAG_ENABLED` | Python | No | `true` | Enable/disable RAG |
| `CHROMA_PERSIST_DIR` | Python | No | `./chroma_data` | ChromaDB storage path |

## RAG Pipeline

The RAG pipeline grounds LLM diagnoses in real Linux kernel documentation:

1. **Documentation** — 5 markdown files covering kernel modules, modprobe, module loading, dependencies, common errors, and NVIDIA troubleshooting (~5,000 words total).
2. **Chunking** — Documents are split into ~600-char overlapping chunks preserving paragraph boundaries.
3. **Embedding** — Chunks are embedded using `all-MiniLM-L6-v2` (384-dimensional vectors).
4. **Storage** — Embeddings stored in ChromaDB with source metadata (file, title, section).
5. **Retrieval** — Diagnostic evidence is transformed into a focused query; top-5 similar chunks are retrieved via cosine similarity.
6. **Augmentation** — Retrieved documentation is injected into the LLM prompt alongside the diagnostic evidence.

The RAG store is populated automatically on first startup. Documentation is in `ai_service/docs/`.
 
## Diagnostic & Troubleshooting Workflow

<p align="center">
  <img src="docs/diagrams/workflow.svg" alt="Kernel Module Diagnostic Lifecycle Workflow" width="100%" />
</p>

<p align="center">
  <em>Interactive version with animated trace: <a href="docs/diagrams/workflow.html"><b>docs/diagrams/workflow.html</b></a> (source: <a href="docs/diagrams/workflow.json">workflow.json</a>)</em>
</p>

The diagnostic pipeline spans 4 core lanes across intake, host telemetry, AI ingestion, semantic RAG matching, LLM reasoning, and fail-closed security recovery.

## Testing

### Go Tests

```bash
go test ./... -v
```

Tests cover:
- Module name validation (valid/invalid inputs)
- Health endpoint
- Auth flows (missing token, wrong token, missing env var)
- Diagnose endpoint (invalid module, missing AI service, valid request)

### Python Tests

```bash
cd ai_service
source .venv/bin/activate
python -m pytest tests/ -v
```

40 tests covering:
- Pydantic model validation
- `/health` and `/analyze` endpoint flows
- Auth and validation error handling
- LLM client request formatting, markdown fence stripping, RAG context injection
- LLM response validation (missing fields, invalid JSON)
- Document loading and chunking
- RAG query construction from evidence
- ChromaDB store lifecycle (init → populate → query)

## Project Structure

```
kernel-module-manager-ai/
├── main.go                          # Go entrypoint
├── go.mod / go.sum
├── internal/server/
│   ├── api.go                       # HTTP handlers + router
│   └── api_test.go                  # Handler tests
├── modules/
│   ├── module_manager.go            # modprobe/rmmod operations
│   ├── diagnostics.go               # System diagnostic collection
│   └── diagnostics_test.go          # Validation tests
├── ai_service/
│   ├── pyproject.toml               # Python project config
│   ├── requirements.txt
│   ├── main.py                      # Legacy entrypoint (redirects to app.main)
│   ├── app/
│   │   ├── main.py                  # FastAPI app + RAG initialization
│   │   ├── config.py                # Environment-based configuration
│   │   ├── models.py                # Pydantic request/response models
│   │   ├── routers/
│   │   │   └── analyze.py           # /analyze endpoint
│   │   ├── services/
│   │   │   ├── llm_client.py        # Async httpx LLM client
│   │   │   └── rag_service.py       # RAG orchestration
│   │   └── rag/
│   │       ├── documents.py         # Document loading + chunking
│   │       ├── embeddings.py        # Sentence-transformers embeddings
│   │       └── store.py             # ChromaDB vector store
│   ├── docs/                        # Linux kernel documentation for RAG
│   │   ├── kernel_modules.md
│   │   ├── modprobe.md
│   │   ├── module_loading.md
│   │   ├── module_dependencies.md
│   │   ├── common_errors.md
│   │   └── nvidia_troubleshooting.md
│   └── tests/
│       ├── conftest.py              # Shared fixtures
│       ├── test_models.py
│       ├── test_analyze.py
│       ├── test_llm_client.py
│       └── test_rag.py
├── docs/
│   └── diagrams/
│       ├── architecture.html        # Interactive Archify architecture diagram
│       ├── architecture.json        # Architecture diagram specification
│       ├── workflow.html            # Interactive Archify workflow diagram
│       └── workflow.json            # Workflow diagram specification
├── .env.example
└── .gitignore
```

## Security

- **Module name validation** — Regex-enforced alphanumeric + underscore/hyphen, max 128 chars.
- **No command injection** — Module names are validated before use in system commands.
- **AI is read-only** — The AI service only analyzes evidence and returns recommendations. It never executes commands or modifies kernel state.
- **Token auth** — All privileged endpoints require `Authorization: Bearer <token>`.
- **Input limits** — Diagnostic output truncated to 12KB, LLM input to 30KB, LLM response to 100KB.
- **Timeouts** — 3s per diagnostic command, 30s for LLM calls, 35s for Go→Python.
- **No secrets in responses** — Diagnostic data is sanitized before sending to LLM providers.

> **Warning**: Do not expose this service publicly. Bind to `127.0.0.1` and use a firewall. Load/unload operations require a trusted Linux host.

## Limitations

- Linux kernel module operations (load/unload/diagnostics) require a Linux environment. On macOS, diagnostic commands will report errors.
- LLM quality depends on the provider and model. Groq and OpenAI are tested.
- The RAG corpus covers common scenarios but isn't exhaustive. Add domain-specific docs to `ai_service/docs/` and restart.
- The embedding model (`all-MiniLM-L6-v2`) downloads ~80MB on first run.
