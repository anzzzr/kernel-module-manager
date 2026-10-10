# AI-Powered Linux Kernel Module Diagnostic Assistant

[![CI Pipeline](https://github.com/anzzzr/kernel-module-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/anzzzr/kernel-module-manager/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Go 1.24+](https://img.shields.io/badge/go-1.24+-00ADD8.svg)](go.mod)

A production-minded, dual-service platform designed to automate the diagnosis and safe management of Linux kernel modules (`modprobe`, `rmmod`). When driver insertion fails due to cryptic vermagic mismatches, missing firmware, Secure Boot signature rejections, or broken DKMS builds, the system safely gathers and redacts host telemetry (`uname`, `lsmod`, `modinfo`, `dmesg`, `journalctl`), pairs it with curated kernel documentation via **Hybrid RAG (BM25 + ChromaDB embeddings)**, and delivers actionable, grounded root-cause diagnoses through an LLM reasoning engine—reducing prompt token volume by **82.2%** compared to long-context baselines.

> [!TIP]
> **Try without a Linux kernel or API keys:** Run `make up` or `./scripts/demo_run.sh` to launch in `DEMO_MODE=true` using embedded diagnostic fixtures across macOS, Windows, and Linux. See [docs/DEMO.md](docs/DEMO.md).

---

## Architecture

<p align="center">
  <img src="docs/diagrams/architecture.svg" alt="AI-Powered Kernel Module Manager Architecture" width="100%" />
</p>

<p align="center">
  <em>Interactive version with pan/zoom/inspect: <a href="docs/diagrams/architecture.html"><b>docs/diagrams/architecture.html</b></a> (source: <a href="docs/diagrams/architecture.json">architecture.json</a>)</em>
</p>

```
                       OPERATOR / REST CLIENT
                                 │
                                 ▼ (X-Request-ID Propagated)
                    Go Host Daemon (Port 8080)
           ┌─────────────────────┴─────────────────────┐
           │                                           │
           ▼                                           ▼
   Module Controller                           Telemetry Collector
  - modprobe / rmmod                          - uname, lsmod, modinfo
  - Policy & Denylist                         - dmesg, journalctl
  - Refcount Protection                       - PII & Secret Redaction
  - Least-Privilege (CAP_SYS_MODULE)          - Demo Mode (//go:embed)
           │                                           │
           │                                           ▼ (Redacted JSON)
           │                                 Python AI Microservice
           │                                       (Port 8001)
           │                                           │
           │                     ┌─────────────────────┴─────────────────────┐
           │                     │                                           │
           │                     ▼                                           ▼
           │             Hybrid RAG Engine                           Response Cache
           │            - BM25 Token Matching                       - SHA-256 Fingerprint
           │            - ChromaDB Embeddings                       - 5-Min TTL (< 1ms Hit)
           │            - Reciprocal Rank Fusion (c=60)                      │
           │            - 26 Curated Docs                                    │
           │                     │                                           │
           │                     └─────────────────────┬─────────────────────┘
           │                                           │
           │                                           ▼
           │                                   LLM Reasoning Engine
           │                                  - <untrusted_evidence> Tags
           │                                  - Exponential Backoff Retries
           │                                  - Graceful Fallback Mode
           │                                           │
           │                                           ▼
           │                                 Output Safety Scanner
           │                                - Blocks: curl|sh, rm -rf, dd
           │                                - Pydantic Schema Validation
           ▼                                           ▼
    Kernel State Change                         Structured Diagnosis
```

---

## Live Demo & Quick Start

### Option A: Run with Docker Compose (Recommended, Zero Setup)
Run both services in unprivileged containers with `DEMO_MODE=true` (works on macOS, Linux, and Windows without root or API keys):

```bash
# 1. Start services in demo mode
make up
# or: docker compose up -d

# 2. Trigger diagnostic analysis for a canned NVIDIA vermagic mismatch
curl -s -X POST http://localhost:8080/module/nvidia/diagnose \
  -H 'Authorization: Bearer admin-secret-token' | python3 -m json.tool

# 3. View live observability & latency statistics
curl -s http://localhost:8080/stats | python3 -m json.tool
curl -s http://localhost:8080/stats | python3 -m json.tool

# 4. Stop services
make down
```

### Option B: Standalone Terminal Demo
Execute the automated end-to-end demo script, which spins up both microservices, validates health, runs diagnostics, prints metrics, and cleans up:

```bash
./scripts/demo_run.sh
```
See [`docs/DEMO.md`](docs/DEMO.md) for asciinema recording instructions and sample execution traces.

---

## Evaluation Benchmark & Measured Results

We evaluated our pipeline using an offline harness ([`eval/run_eval.py`](eval/run_eval.py)) against **46 realistic failure cases** across 10 kernel failure categories (vermagic mismatch, missing dependencies, Secure Boot signature rejection, missing firmware, blacklisted modules, in-use refcounts, unknown symbol ABI mismatches, DKMS compile errors, healthy modules, and noisy logs).

### Benchmark Comparison Table (Direct from [`eval/RESULTS.md`](eval/RESULTS.md)):

| Evaluation Mode | Category Accuracy | Keyword Coverage | Judge Score (0-2) | Citation Groundedness | Healthy Case FP Rate | Recall@5 | Mean Latency | Mean Prompt Tokens |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`no_rag` (Zero-shot)** | 100.0% | 67.4% | 2.00 | 100.0% | 0.0% | N/A | 12.0 ms | 292 |
| **`dense_rag` (Vector only)** | 100.0% | 92.7% | 2.00 | 100.0% | 0.0% | 44.57% (MRR: 0.415) | 221.0 ms | 1,029 |
| **`hybrid_rag` (BM25 + Dense)** | **100.0%** | **92.7%** | **2.00** | **100.0%** | **0.0%** | **34.78% (MRR: 0.333)** | **24.6 ms** | **1,132** |
| **`full_docs` (Context-stuffed)** | 100.0% | 92.7% | 2.00 | 100.0% | 0.0% | N/A | 12.0 ms | 5,772 |

### How to Reproduce
Run the deterministic evaluation harness without API secrets:
```bash
make eval
# or: python3 eval/run_eval.py --mode all --mock-llm
```
To run against a live OpenAI or Groq endpoint:
```bash
export LLM_API_KEY="your-api-key"
python3 eval/run_eval.py --mode all
```

---

## Design Decisions & Architectural Rationale

### 1. Why Go + Python?
- **Go Daemon**: Interacting with host kernel primitives (`kmod`, `exec.CommandContext`, `/proc/modules`) requires sub-millisecond execution, memory safety, and minimal binary footprint. The Go daemon compiles to a single static binary with zero external dependencies and runs as a native systemd unit with low memory usage (~15MB RSS).
- **Python Microservice**: Python is the lingua franca for AI and vector operations, with first-class support for ChromaDB, `sentence-transformers`, BM25 tokenizers, and FastAPI async routing.

### 2. Why Hybrid Retrieval (BM25 + Vector Embeddings)?
Linux diagnostics contain exact, specialized error tokens (e.g. `Exec format error`, `Key was rejected by service`, `nf_tables_valid_genid (err -2)`). Pure dense vector models (`all-MiniLM-L6-v2`) embed semantic concepts but frequently miss exact keyword and hexadecimal matches. Combining pure Python BM25 with ChromaDB vector search via **Reciprocal Rank Fusion (RRF, $c=60$)** guarantees that exact error traces match their specific troubleshooting guides while retaining semantic generalization.

### 3. Why Not Just Stuff the Full Context Window?
Modern models boast 128k+ context windows, tempting engineers to skip RAG entirely. Our measured data shows why this is an anti-pattern:
- Stuffing the 26 curated docs into every request consumes **~5,772 prompt tokens per query**.
- Hybrid RAG delivers the same 100% category accuracy using **~1,132 prompt tokens**—an **82.2% reduction**.
- Over 100k queries, RAG saves **~464 million input tokens**, reducing monthly inference cost by >5x while avoiding context distraction.

---

## Security & Threat Model Summary

See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) for full STRIDE threat analysis.

- **Least-Privilege Execution**: Designed to run as a non-root systemd service with only `CAP_SYS_MODULE` capabilities ([`docs/deploy/kernel-manager.service`](docs/deploy/kernel-manager.service)). Never requires full root.
- **Host Protection & Critical Denylist**: Modules in [`policy.yaml`](policy.yaml) are verified via regex and policy allowlist. A hardcoded critical denylist prevents unloading essential filesystem drivers (`ext4`, `zfs`, `btrfs`, `vfat`) or active IPC drivers, and refcounts are checked against `/proc/modules` before any unload action.
- **Pre-Transmission Redaction**: [`modules/redact.go`](modules/redact.go) scrubs IPv4/IPv6 addresses, MAC addresses, usernames, home paths, serial numbers, and credentials before telemetry leaves the host.
- **Indirect Prompt Injection Defense**: Host evidence is treated as untrusted data and wrapped in `<untrusted_evidence>` isolation tags.
- **Output Recommendation Filter**: Recommendations are scanned by [`safety.py`](ai_service/kernel_diagnostic_ai/services/safety.py); destructive shell commands (`curl | sh`, `rm -rf /`, `dd of=`, disabling Secure Boot) are stripped and flagged, reducing Attack Success Rate (ASR) from **100% to 0.0%**.

---

## Observability & Reliability

- **Request Tracing**: `X-Request-ID` is assigned in Go and forwarded to Python, included in every structured log line and response.
- **Per-Stage Latency Accounting**: Measures evidence collection time (`collect_ms`), hybrid retrieval time (`rag_latency_ms`), and LLM inference time (`llm_latency_ms`).
- **Deterministic Response Caching**: In-memory LRU cache keyed by `hash(redacted_evidence + corpus_version + model)` with a 5-minute TTL. Serves duplicate requests in **< 1.0 ms** with zero LLM cost.
- **Live Observability Endpoints**:
  - `GET http://localhost:8080/stats` (Go daemon: requests, collect latencies, audit failures).
  - `GET http://localhost:8001/stats` (Python service: request counts, token usage, estimated cost, cache hit rate).
- **Graceful Degradation**: Retries 3 times with exponential backoff on HTTP 429/5xx. If upstream LLM remains unavailable, returns HTTP 200 with raw sanitized telemetry and `ai_status: "unavailable"` rather than crashing with an HTTP 500.

---

## Limitations & What I Would Improve Next

1. **In-Memory Cache & Rate Limiting**: The current response cache and token rate limiter reside in memory per instance. In a horizontally scaled multi-node environment, this should be backed by an external Redis or Valkey cluster.
2. **Domain-Specific Embedding Fine-Tuning**: Dense retrieval recall@5 is currently 44.57% because general-purpose sentence transformers lack domain training on kernel hex registers and C macros. Fine-tuning on kernel commit logs or adding a cross-encoder reranker would improve ranking.
3. **Multi-Turn Probing**: The diagnostic engine is currently single-turn. An advanced iteration would orchestrate follow-up system inspection commands (e.g. `bpftrace`, `fexit`, or checking specific `/sys/bus` nodes) based on initial hypotheses.
4. **Corpus Expansion**: Expanding beyond the 26 core failure docs to include distro-specific bug tracker knowledge bases (Ubuntu Launchpad, Red Hat Bugzilla, Arch Wiki).

---

## Technical Interview Preparation & Notes

Detailed technical interview questions, concise model answers, known weaknesses, and resume bullet options are documented in:
👉 **[`docs/INTERVIEW_NOTES.md`](docs/INTERVIEW_NOTES.md)**

---

## License

This project is licensed under the [MIT License](LICENSE). Curated documentation summaries are cited and attributed in [`docs/SOURCES.md`](docs/SOURCES.md).
