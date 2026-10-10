# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-10-11

### Added
- **Evaluation Harness**: Automated offline evaluation suite in `eval/run_eval.py` benchmarking `no_rag`, `rag` (hybrid top-k), and `full_docs` across 46 realistic Linux kernel failure cases.
- **Hybrid RAG Pipeline**: Lexical BM25 search combined with ChromaDB dense semantic vectors (`all-MiniLM-L6-v2`) via Reciprocal Rank Fusion (RRF).
- **Expanded Documentation Corpus**: 26 curated Linux kernel failure guides with source URLs and structured metadata.
- **Security Hardening**:
  - Configuration policy (`policy.yaml`) with module allowlisting and critical driver denylists (filesystem, storage, and networking).
  - Dry-run mode (`?dry_run=true`) for privileged module operations.
  - Constant-time token authentication comparison with separate read/write authorization scopes.
  - Pre-egress regex telemetry redaction scrubbing IPs, MACs, hostnames, usernames, and UUIDs.
  - Prompt injection shielding wrapping untrusted kernel evidence in `<evidence>` tags.
  - Output safety filter scanning AI recommendations for dangerous commands (`rm -rf`, `dd`, `mkfs`, raw scripts).
  - Append-only structured audit logger recording caller token ID, module name, and execution result.
- **Observability**: End-to-end `X-Request-ID` tracing, stage-level latency instrumentation, and `/stats` metrics endpoints.
- **Resilience**: In-memory SHA-256 fingerprint response cache (5-minute TTL) and 3x exponential backoff retries with graceful degraded fallback.
- **Packaging & CI**: Multi-stage unprivileged Dockerfiles, `docker-compose.yml` with `DEMO_MODE=true`, and GitHub Actions CI workflow covering Go, Python, and offline evaluation smoke tests.
- **Archify Visuals**: Four revision-pinned interactive architecture, sequence, data flow, and workflow diagrams.

### Changed
- Refactored Go REST API to gorilla/mux with structured error handlers.
- Modularized Python AI service into `kernel_diagnostic_ai` package with strict Pydantic schemas.
- Replaced regex-only module validation with fail-closed allowlist/denylist policy.

### Security
- Restricted live host execution to least-privilege `CAP_SYS_MODULE` systemd unit specification (`docs/deploy/kernel-manager.service`).
- Guaranteed fail-closed behavior on module unloading when module refcount > 0.
