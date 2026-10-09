# Kernel Diagnostic AI (`kernel-diagnostic-ai`)

AI-Powered Linux Kernel Module Diagnostic Assistant backed by Retrieval-Augmented Generation (RAG) and ChromaDB.

## Features

- **Automated Kernel Telemetry Analysis**: Diagnoses Linux kernel module loading issues (`vermagic` mismatch, missing dependencies, device driver conflicts, Secure Boot issues).
- **Embedded Technical Knowledge Base**: Bundles curated Linux kernel module documentation (modprobe, modinfo, dependencies, common errors, NVIDIA GPU troubleshooting).
- **Local Semantic Retrieval**: Uses Sentence-Transformers (`all-MiniLM-L6-v2`) and ChromaDB vector store for accurate, hallucination-free retrieval.
- **Microservice & CLI**: Exposes both an authenticated FastAPI REST microservice and an easy-to-use command-line interface (`kernel-ai`).
- **OpenAI & Groq Compatible**: Connects to any OpenAI-compatible LLM endpoint (Groq, OpenAI, Ollama, vLLM).

## Installation

```bash
pip install kernel-diagnostic-ai
```

Or install in editable mode from source:

```bash
cd ai_service
pip install -e .
```

## CLI Usage

### Start Diagnostic REST API Server

```bash
export LLM_API_KEY="your-api-key"
# Optional: export LLM_BASE_URL="https://api.groq.com/openai/v1"
# Optional: export LLM_MODEL="llama-3.3-70b-versatile"
# Optional: export AI_SERVICE_TOKEN="shared-secret-token"

kernel-ai serve --host 0.0.0.0 --port 8001
```

### Inspect RAG Vector Store

```bash
kernel-ai rag-status
```

### Run Direct Diagnosis

```bash
kernel-ai diagnose --module nvidia
```

Or pass pre-collected evidence from a JSON file:

```bash
kernel-ai diagnose --module nvidia --evidence-file sample_evidence.json
```

## Python Library Usage

```python
import asyncio
from kernel_diagnostic_ai.models import Evidence
from kernel_diagnostic_ai.services.rag_service import retrieve_context
from kernel_diagnostic_ai.services.llm_client import call_llm

evidence = Evidence(
    module="nvidia",
    commands={
        "uname": "5.15.0-91-generic",
        "lsmod": "",
        "modinfo": "modinfo: ERROR: Module nvidia not found.",
    },
    errors={"modprobe": "FATAL: Module nvidia not found."},
)

async def main():
    # 1. Retrieve grounded kernel docs
    context, docs = retrieve_context(evidence)
    
    # 2. Query reasoning model
    diagnosis = await call_llm(evidence.model_dump_json(), context)
    print(diagnosis)

asyncio.run(main())
```

## License

MIT License
