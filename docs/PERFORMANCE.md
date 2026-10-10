# System Performance & Operational Characteristics

This document details the empirically measured latency breakdown, token consumption, caching efficiency, and cost profiles of `kernel-module-manager` across evaluation and operational workloads.

All figures presented below derive directly from reproducible benchmark runs recorded in [`eval/RESULTS.md`](../eval/RESULTS.md).

---

## 1. End-to-End Latency Breakdown by Stage

Diagnostic request latency spans four distinct phases:

```
[ Client Request ]
       │
       ▼ (Phase 1: Go Diagnostic Telemetry Collection)
       ├─ uname, lsmod, modprobe --show-depends, modinfo
       ├─ dmesg (tail 50) & journalctl (last 30)
       ├─ Redaction filter (IPs, MACs, secrets)
       │  ==> Mean Duration: ~10 - 15 ms
       ▼
[ Python AI Microservice (X-Request-ID Propagated) ]
       │
       ├─ (Phase 2: RAG Context Retrieval)
       │  ├─ Hybrid BM25 keyword search + ChromaDB vector lookup
       │  ├─ Reciprocal Rank Fusion (c=60)
       │  ==> Mean Duration: ~8 - 12 ms
       │
       ├─ (Phase 3: LLM Inference & Reasoning)
       │  ├─ OpenAI / Groq completions call (model: gpt-4o-mini / llama-3.3-70b)
       │  ├─ Exponential backoff retries (on 429/5xx)
       │  ==> Mean Network & Inference Duration: ~450 - 1,200 ms (Live API)
       │
       └─ (Phase 4: Output Validation & Safety Scanning)
          ├─ Pydantic schema validation
          ├─ Recommendation pattern scanner (pipe-to-shell, disk overwrites)
          ==> Mean Duration: < 1 ms
```

### Measured Pipeline Latencies:
| Pipeline Phase | Mean Latency | Percentage of Request |
|:---|:---:|:---:|
| **Go Host Evidence Collection & Redaction** | ~12.5 ms | ~1.2% |
| **Python Hybrid RAG Retrieval (ChromaDB + BM25)** | ~10.2 ms | ~1.0% |
| **LLM Inference & Network Transmission** | ~950.0 ms | ~97.7% |
| **Output Safety Scanning & Schema Parsing** | ~0.4 ms | < 0.1% |
| **Total End-to-End Request** | **~973.1 ms** | **100%** |

*(Note: In mock/offline CI evaluation mode where LLM network transit is mocked, total software pipeline latency is ~22 ms).*

---

## 2. Token Consumption & Inference Cost Analysis

A central architectural decision was determining whether to retrieve top-$k$ documentation sections via RAG or inject the full documentation corpus into modern large-context LLM windows:

| Mode | Mean Input Prompt Tokens | Est. Cost / 1k Requests (`gpt-4o-mini`) | Est. Cost / 1k Requests (`llama-3.3-70b`) |
|:---|:---:|:---:|:---:|
| **`no_rag` (Zero-shot)** | ~292 tokens | $0.04 | $0.17 |
| **`dense_rag` (top-5 chunks)** | **~1,029 tokens** | **$0.15** | **$0.61** |
| **`hybrid_rag` (top-5 RRF)** | **~1,132 tokens** | **$0.17** | **$0.67** |
| **`full_docs` (All 26 docs stuffed)** | **~5,772 tokens** | **$0.87** | **$3.41** |

### Key Economic Finding:
Stuffing the full documentation corpus into every diagnostic call increases input token volume by **over 5x** (~5,772 tokens vs ~1,029 tokens).
Deploying vector/hybrid RAG reduces prompt token consumption by **82.2%**, saving significant inference cost at scale while maintaining identical category diagnostic accuracy (100.0%) and zero negative control false alarms.

---

## 3. Response Caching & Resilience

### SHA-256 Fingerprint Caching
Repeated requests with identical redacted diagnostic telemetry, corpus versions, and model configurations are served directly from an in-memory TTL cache (`kernel_diagnostic_ai/services/cache.py`).
- **Cache Hit Latency**: **< 1.0 ms**
- **Token Consumption on Hit**: **0 tokens ($0.00 cost)**

### Fallback Graceful Degradation
If the third-party LLM provider encounters unrecoverable rate limits (HTTP 429) or cloud downtime (HTTP 5xx) after 3 exponential backoff attempts:
- The system **does not return an HTTP 500 failure**.
- It returns an HTTP 200 payload containing the sanitized host evidence and sets `ai_status: "unavailable"`.
- The system administrator can immediately review raw host telemetry without system interruption.

---

## 4. Observability Endpoint Design: Why `/stats` Was Chosen

Both services expose lightweight, zero-dependency JSON metrics endpoints:
- Go Daemon: `GET http://127.0.0.1:8080/stats`
- Python AI Service: `GET http://127.0.0.1:8001/stats`

**Design Decision Rationale**:
Rather than pulling in heavyweight third-party dependencies (`prometheus_client` in Python or Prometheus Go client libraries), we implemented native, thread-safe `/stats` endpoints. This keeps the daemon lightweight and zero-dependency, suitable for edge Linux systems while still providing request counts, cache hit ratios, error counts, and latency averages. In Kubernetes environments, these JSON metrics can be scraped and converted via Prometheus exporter sidecars if required.
