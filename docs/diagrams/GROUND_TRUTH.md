# Ground Truth Architecture Mapping

This document maps every diagram node across the four Archify diagrams to concrete, existing source files in the repository. Per the project's strict engineering rules, every node corresponds to a real code component or verified operational asset—no hypothetical or unbuilt services are included.

Repository URL: `https://github.com/anzzzr/kernel-module-manager`  
Revision: `33afc431234b80a6046093b899f04f21e766ad35`

---

## 1. Runtime Architecture (`docs/diagrams/architecture.json`)

| Component ID | Node Label | Type | Source File(s) & Lines | Description |
|---|---|---|---|---|
| `client` | SRE / Operator | `external` | `scripts/demo_run.sh:1-35` | HTTP REST consumer invoking diagnostic and module operations |
| `router` | Go REST Router | `backend` | `internal/server/api.go:30-80` | Gorilla/mux router on `:8080` with routing, timeouts, and request ID middleware |
| `auth_guard` | Policy & Auth Guard | `security` | `internal/server/api.go:130-170`, `modules/policy.go:30-80` | Constant-time bearer token check, allowlist, and critical driver denylist |
| `collector` | Host Telemetry Collector | `backend` | `modules/diagnostics.go:20-65`, `modules/demo.go:15-55` | Executes safe read-only commands (`lsmod`, `dmesg`, `modinfo`, `uname`) or loads mock fixtures in `DEMO_MODE` |
| `redactor` | Evidence Redactor | `security` | `modules/redact.go:15-50` | Redacts IPs, MAC addresses, hostnames, usernames, and serials from kernel logs before egress |
| `audit_sink` | Audit Logger | `backend` | `internal/server/audit.go:20-60` | Structured append-only audit logger capturing caller token ID, module, action, and result |
| `kernel_mod` | Linux Kernel Subsystem | `external` | `modules/module_manager.go:15-38` | Host kernel subsystem invoked via `exec.CommandContext` (`modprobe`, `rmmod`) |
| `ai_ingress` | FastAPI Service | `backend` | `ai_service/kernel_diagnostic_ai/main.py:25-70` | FastAPI service on `:8001` receiving `/analyze` requests with service token auth |
| `response_cache` | Response Cache | `database` | `ai_service/kernel_diagnostic_ai/services/cache.py:15-60` | In-memory cache keyed on hash(evidence + corpus_version + model) with 5m TTL |
| `hybrid_rag` | Hybrid RAG Engine | `backend` | `ai_service/kernel_diagnostic_ai/services/rag_service.py:25-85`, `ai_service/kernel_diagnostic_ai/rag/bm25.py:20-75` | BM25 exact error matching + ChromaDB dense embeddings fused with Reciprocal Rank Fusion |
| `vector_store` | ChromaDB Store | `database` | `ai_service/kernel_diagnostic_ai/rag/store.py:25-80` | Vector store indexing 26 curated Linux kernel failure docs with `all-MiniLM-L6-v2` embeddings |
| `llm_client` | Resilient LLM Client | `backend` | `ai_service/kernel_diagnostic_ai/services/llm_client.py:30-100` | OpenAI/Groq async client with 3x exponential backoff, timeout, and degraded-mode fallback |
| `safety_filter` | Safety Filter | `security` | `ai_service/kernel_diagnostic_ai/services/safety.py:15-55` | Regex scanner inspecting LLM recommendations for dangerous commands (`rm -rf`, `dd`, `mkfs`, raw scripts) |
| `cloud_llm` | Cloud LLM Provider | `cloud` | `ai_service/kernel_diagnostic_ai/services/llm_client.py:65-115` | External LLM API (OpenAI / Groq) executing ChatCompletions |

---

## 2. POST /diagnose Execution Sequence (`docs/diagrams/diagnose-sequence.json`)

| Participant ID | Participant Label | Type | Source File(s) & Lines | Role in Sequence |
|---|---|---|---|---|
| `sre` | SRE Operator | `external` | `scripts/demo_run.sh:1-35` | Issues `POST /diagnose` with bearer token |
| `go_router` | Go Gateway | `backend` | `internal/server/api.go:30-80` | Assigns `X-Request-ID`, checks auth, dispatches diagnosis |
| `policy_sec` | Policy Engine | `security` | `modules/policy.go:30-80` | Validates regex module syntax and allowlist |
| `collector_mod`| Diagnostic Collector | `backend` | `modules/diagnostics.go:20-65` | Gathers evidence (`uname`, `dmesg`, `lsmod`) |
| `redactor_mod` | Redaction Engine | `security` | `modules/redact.go:15-50` | Scrubs PII and network identifiers from evidence |
| `ai_api` | FastAPI Analyzer | `backend` | `ai_service/kernel_diagnostic_ai/routers/analyze.py:20-75` | Handles `/analyze`, checks cache, orchestrates retrieval |
| `cache_store` | Diagnosis Cache | `database` | `ai_service/kernel_diagnostic_ai/services/cache.py:15-60` | Checks SHA-256 fingerprint; returns cached diagnosis on hit |
| `rag_engine` | Hybrid Retriever | `backend` | `ai_service/kernel_diagnostic_ai/services/rag_service.py:25-85` | Queries BM25 and ChromaDB, calculates reciprocal rank scores |
| `llm_cloud` | LLM Provider | `cloud` | `ai_service/kernel_diagnostic_ai/services/llm_client.py:65-115` | Generates structured diagnostic JSON (or triggers degraded mode) |

---

## 3. Security Data Flow Pipeline (`docs/diagrams/security-dataflow.json`)

| Stage | Node ID | Node Label | Type | Source File(s) & Lines | Functionality |
|---|---|---|---|---|---|
| 0: Telemetry | `raw_evidence` | Raw Kernel Evidence | `external` | `modules/diagnostics.go:20-65` | Diagnostic output from `dmesg`, `modinfo`, and `journalctl` |
| 1: Sanitization | `redactor_node` | Regex Redactor | `security` | `modules/redact.go:15-50` | Strips IPv4/v6, MACs, `/home` paths, usernames, hostnames, UUIDs |
| 1: Sanitization | `injection_guard`| Untrusted Delimiter | `security` | `ai_service/kernel_diagnostic_ai/routers/analyze.py:35-65` | Encloses evidence in `<evidence>` tags with system instructions: untrusted data |
| 2: Retrieval | `bm25_dense` | Hybrid Retrieval (RRF)| `backend` | `ai_service/kernel_diagnostic_ai/services/rag_service.py:30-80` | Fuses exact error traces with semantic vector similarity |
| 3: Reasoning | `llm_inference`| Sandboxed LLM Call | `cloud` | `ai_service/kernel_diagnostic_ai/services/llm_client.py:65-115` | Structured JSON generation using bounded prompt instructions |
| 4: Egress Gate | `safety_filter_node`| Command Safety Guard | `security` | `ai_service/kernel_diagnostic_ai/services/safety.py:15-55` | Scans recommendations for destructive system commands |
| 4: Egress Gate | `pydantic_val` | Schema Validation | `backend` | `ai_service/kernel_diagnostic_ai/models.py:15-40` | Validates strict JSON schema (`root_cause`, `confidence`, `recommendations`) |
| 4: Egress Gate | `audit_sink` | Audit Log Record | `backend` | `internal/server/audit.go:20-60` | Logs action ID, caller token ID, module, and response status |

---

## 4. Evaluation & CI Pipeline (`docs/diagrams/eval-and-ci.json`)

| Lane / Stage | Node ID | Node Label | Type | Source File(s) & Lines | Functionality |
|---|---|---|---|---|---|
| Evaluation | `case_corpus` | 46 Curated Eval Cases | `database` | `eval/cases/case_01_vermagic_nvidia.json:1-25` | Covers 8 failure categories + healthy modules + noisy logs |
| Evaluation | `eval_harness` | `run_eval.py` Engine | `backend` | `eval/run_eval.py:40-150` | Executes benchmarks across `no_rag`, `rag`, and `full_docs` modes |
| Evaluation | `metrics_engine`| Metric Calculator | `backend` | `eval/metrics.py:15-80` | Computes recall@k, MRR, category accuracy, and keyword coverage |
| Evaluation | `results_table`| `RESULTS.md` Ledger | `frontend` | `eval/RESULTS.md:1-50` | Authoritative benchmark score matrix and reproduction instructions |
| CI Workflows | `go_ci_job` | Go Test & Sec Audit | `security` | `.github/workflows/ci.yml:12-28` | `go test ./... -v -race`, `go vet`, redaction and security tests |
| CI Workflows | `python_ci_job`| Python Lint & Test | `backend` | `.github/workflows/ci.yml:30-52` | `ruff check`, `ruff format --check`, `pytest services/ tests/` |
| CI Workflows | `eval_smoke_job`| Eval Smoke Test | `backend` | `.github/workflows/ci.yml:54-75` | Automated offline evaluation run using deterministic Mock LLM |
