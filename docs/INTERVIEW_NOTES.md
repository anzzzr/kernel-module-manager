# Technical Interview Guide & Engineering Notes

This document provides concise, technically honest interview answers covering the architectural, evaluation, security, and systems engineering decisions in `kernel-module-manager`.

All performance, accuracy, and latency numbers cited below are derived from empirical benchmark runs documented in [`eval/RESULTS.md`](../eval/RESULTS.md) and [`docs/PERFORMANCE.md`](PERFORMANCE.md).

---

## 1. 15 Likely Interview Questions & Model Answers

### Q1: What problem does this project solve, and who is the target user?
> **Answer**: Linux kernel module insertion and removal failures (e.g., `modprobe: Exec format error`, `Required key not available`, missing firmware, symbol mismatches) produce cryptic, low-level error codes spread across `dmesg`, `modinfo`, `journalctl`, and dependency trees. Systems administrators, DevOps engineers, and SREs often waste hours chasing DKMS compile logs or Secure Boot MOK keys. This project combines a low-overhead host daemon that safely captures and sanitizes Linux kernel telemetry with an AI microservice that retrieves verified kernel documentation and generates structured root-cause analyses and remediation steps.

### Q2: Why use RAG instead of simply stuffing the entire documentation corpus into a large LLM context window?
> **Answer**: We empirically benchmarked both approaches on 46 failure cases across 10 failure categories. Stuffing all 26 curated documentation files into prompt context (`full_docs`) consumed **~5,772 input prompt tokens per query**, whereas our hybrid RAG pipeline (`top_k=5`) consumed **~1,132 prompt tokens**—an **82.2% reduction in prompt token volume** while maintaining identical **100% diagnostic category accuracy**. At scale (e.g., 100k queries/month), RAG drops monthly API inference costs from ~$341 to ~$67 on models like `llama-3.3-70b`, and prevents context distraction while ensuring sub-millisecond retrieval latency (~10 ms).

### Q3: Why split the system into a Go daemon and a Python FastAPI service rather than writing everything in one language?
> **Answer**: Separation of concerns and platform affinity:
> - **Go**: Best suited for a host system daemon interacting directly with Linux OS primitives, `procfs`, `sysfs`, and `exec.CommandContext`. It compiles to a single, lightweight statically linked binary with zero runtime dependencies, predictable sub-millisecond execution, and rock-solid concurrency.
> - **Python**: The standard ecosystem for modern AI/ML workloads, providing native integration with ChromaDB, Hugging Face `sentence-transformers`, BM25, and Pydantic validation.
>
> They communicate over HTTP with strict schema contracts, request-ID propagation, and independent containerization.

### Q4: How do you handle retrieval when Linux errors contain exact error strings like "Unknown symbol" vs conceptual queries?
> **Answer**: Pure vector embedding search often struggles with specialized kernel symbol names or hex error codes (e.g., `nf_tables_valid_genid (err -2)` or `Key was rejected by service`). We implemented **Hybrid Retrieval** combining a pure Python BM25 index for exact token/keyword matching and ChromaDB (`all-MiniLM-L6-v2`) for semantic similarity, merged via **Reciprocal Rank Fusion (RRF, $c=60$)**. BM25 guarantees that exact error traces match the relevant troubleshooting guides, while vector search handles fuzzy symptoms.

### Q5: How did you evaluate RAG quality, and what metrics did you track?
> **Answer**: We built an offline evaluation harness (`eval/run_eval.py`) with 46 benchmark cases covering 10 distinct failure categories (vermagic mismatch, missing dependencies, Secure Boot key rejection, missing firmware, blacklisted drivers, in-use refcounts, ABI symbol mismatch, DKMS compiler errors, healthy modules, and noisy logs).
> We tracked:
> 1. **Retrieval**: Recall@5 and Mean Reciprocal Rank (MRR).
> 2. **Diagnosis**: Category Accuracy (100.0%) and Keyword Coverage (92.7% vs 67.4% for zero-shot `no_rag`).
> 3. **Faithfulness**: Citation Groundedness (100% of cited docs exist in repository corpus).
> 4. **Negative Controls**: False Positive Rate on healthy modules (0.0%).
> 5. **LLM-as-a-Judge**: Calibrated 0–2 score rubric with fixed criteria.

### Q6: How did you validate that your LLM-as-a-judge metric was reliable?
> **Answer**: We conducted a calibration study on a 10-case hand-verified subset comparing the automated judge against deterministic category and keyword match scores. The judge achieved **90% direct agreement** with deterministic rules. The single disagreement occurred on an edge case where the model accurately identified the root cause but phrased remediation steps with conservative uncertainty.

### Q7: How do you prevent malicious `dmesg` logs from hijacking the LLM (Indirect Prompt Injection)?
> **Answer**: Telemetry logs are inherently untrusted user/hardware input. We implemented two defensive layers:
> 1. **Ingestion Isolation**: Evidence is enclosed in strict `<untrusted_evidence>` XML boundaries accompanied by system prompt directives instructing the model to treat content strictly as passive telemetry, never instructions.
> 2. **Output Safety Filtering**: Generated recommendations pass through a regex safety scanner (`sanitize_recommendations`) that detects and flags dangerous shell pipes (`curl | sh`), recursive filesystem deletions (`rm -rf`), raw disk overwrites (`dd of=`), and disabling Secure Boot (`mokutil --disable-validation`). In our evaluation tests (`eval/test_injection.py`), the safety filter reduced Attack Success Rate (ASR) from **100.0% to 0.0%**.

### Q8: How is host kernel safety enforced on the Go side?
> **Answer**: Module names are validated against strict alphanumeric regex (`^[a-zA-Z0-9_][a-zA-Z0-9_-]{0,127}$`) and checked against an allowlist/denylist policy (`policy.yaml`). To prevent accidental host bricking, a hardcoded **critical system denylist** strictly forbids unloading filesystem drivers (`ext4`, `zfs`, `btrfs`, `vfat`) or essential networking/IPC modules under any circumstances. Additionally, we check `/proc/modules` and `lsmod` refcounts to reject unloading modules actively in use.

### Q9: Does the Go daemon require root privileges?
> **Answer**: No. By design, the daemon never requires full `root` access. In production, it runs as an unprivileged service account granted only the specific Linux capability `CAP_SYS_MODULE` via systemd (`AmbientCapabilities=CAP_SYS_MODULE` in `docs/deploy/kernel-manager.service`). Our Docker container also runs as an unprivileged non-root user (UID 10001) by default.

### Q10: How do you protect sensitive internal system data before sending logs to an external LLM?
> **Answer**: Before evidence leaves the Go daemon, [`modules/redact.go`](../modules/redact.go) executes regex redaction over all command outputs, sanitizing:
> - IPv4 and IPv6 addresses.
> - Hardware MAC addresses.
> - User home directory paths and usernames (`/home/<user>/...` $\to$ `/home/[USER]/...`).
> - Hardware serial numbers and drive UUIDs.
> - Bearer tokens and apparent secret keys.

### Q11: How does the system behave when the LLM provider experiences cloud downtime or rate limits (HTTP 429/5xx)?
> **Answer**: In systems operations, partial data is far better than a total failure. If the LLM provider fails after 3 exponential backoff attempts (1.0s, 2.0s, 4.0s):
> - The service **does not return an HTTP 500 error**.
> - It degrades gracefully, returning an HTTP 200 payload containing the sanitized system evidence and sets `ai_status: "unavailable"`.
> - Administrators immediately receive raw command traces rather than an unhelpful 500 Internal Server Error.

### Q12: How do you optimize latency and cost for repeated queries?
> **Answer**: We implemented deterministic SHA-256 fingerprint response caching in [`cache.py`](../ai_service/kernel_diagnostic_ai/services/cache.py), keyed on `hash(redacted_evidence + corpus_version + model_name)` with a 5-minute TTL. Because evidence is sanitized of ephemeral timestamps before hashing, identical system diagnostic requests hit the cache in **< 1.0 ms** with **0 tokens consumed ($0.00 cost)**.

### Q13: Why did you implement a native `/stats` endpoint instead of pulling in Prometheus client libraries?
> **Answer**: Minimizing binary size and dependency overhead. The Go host daemon is a lightweight system agent; pulling in heavy telemetry libraries adds binary bloat and external dependency risks. We used lock-free atomic counters (`sync/atomic`) in Go and an in-memory accumulator in Python to expose standard JSON metrics (`GET /stats`) with zero external dependencies.

### Q14: How did you enable testing on macOS and Windows without requiring a live Linux kernel?
> **Answer**: We built `DEMO_MODE=true` into both services. In Go, we embedded realistic failure fixtures directly into the binary using Go 1.16+ `//go:embed`. When `DEMO_MODE=true` is set, `Diagnose()` returns canned telemetry matching real Linux bug reports, and `LoadModule`/`UnloadModule` simulate execution. The Python service provides a mock LLM mode, enabling complete end-to-end verification via `make up` or `./scripts/demo_run.sh` on any OS.

### Q15: How did you determine the optimal chunk size and top-$k$ for retrieval?
> **Answer**: We ran a hyperparameter ablation study across chunk sizes (400, 600, 800 characters) and top-$k$ values (3, 5, 7). Chunk size 600 with top-$k=5$ yielded the optimal balance: 100% category accuracy, maximum keyword coverage (92.7%), and manageable prompt token volume (~1,029 tokens), whereas smaller chunk sizes split section headings away from code examples, degrading keyword coverage.

---

## 2. Five Known Weaknesses (To Be Upfront About)

1. **Compact Documentation Corpus (26 Curated Docs)**:
   - *Reality*: While 26 documents thoroughly cover the 10 benchmark failure categories (~24,000 words), real-world kernel issues span thousands of proprietary out-of-tree drivers, hardware errata, and vendor-specific bug trackers. RAG's true superiority over full-context stuffing becomes even more pronounced as the corpus scales to thousands of documents.
2. **Dense Retrieval Recall Limitations on Hex/Macro Strings**:
   - *Reality*: Dense semantic retrieval alone achieved a Recall@5 of 44.57% because general-purpose sentence transformers (`all-MiniLM-L6-v2`) are not pre-trained on Linux kernel C macros and hex register dumps. While our BM25 hybrid fusion compensates for exact terms, fine-tuning an embedding model or adding a cross-encoder reranker would improve ranking precision.
3. **Single-Turn Diagnosis (Non-Interactive)**:
   - *Reality*: The diagnostic pipeline is currently single-turn (ingest host evidence $\to$ output diagnosis). In complex debugging scenarios, a senior engineer often executes follow-up probes (e.g. `bpftrace`, `fexit`, or checking specific `/sys/bus` attributes). The system does not yet orchestrate multi-step interactive probing.
4. **Per-Node In-Memory Cache & Rate Limiting**:
   - *Reality*: The response cache and rate limiter are currently implemented in memory per process. In a horizontally scaled cluster behind a round-robin load balancer, cache hits and rate limit accounting would require an external store like Redis.
5. **Pattern-Based Regex Redaction**:
   - *Reality*: Redaction relies on curated regular expressions for IP, MAC, usernames, and credentials. While fast and zero-overhead, regex cannot identify proprietary company project names or novel token formats without a named entity recognition (NER) model.

---

## 3. Resume Bullet Options (Backed by Measured Data)

### Option 1: Full-Stack / Systems & AI Engineering Focus
> - Engineered an AI-assisted Linux kernel module diagnostic platform (Go + Python/FastAPI) processing `dmesg`, `modinfo`, and `journalctl` telemetry; integrated hybrid RAG (BM25 + ChromaDB) to achieve **100% root-cause category accuracy** across 46 failure benchmark cases while reducing prompt token consumption by **82.2%** (~1,132 vs ~5,772 tokens) compared to full-context baselines.

### Option 2: Machine Learning Systems / RAG Evaluation Focus
> - Built an end-to-end evaluation harness for kernel diagnostic RAG pipelines across 10 failure categories; achieved **92.7% diagnostic keyword coverage**, **0.0% false-positive rate on healthy modules**, and **100% citation groundedness** using Reciprocal Rank Fusion (RRF); calibrated LLM-as-a-judge scoring to **90% agreement** against deterministic metrics.

### Option 3: Production Security & SRE Focus
> - Hardened a privileged Linux systems daemon with least-privilege architecture (`CAP_SYS_MODULE`), regex & allowlist policy enforcement, refcount checks, and automated PII redaction; mitigated indirect prompt injection via delimited context tags and output safety scanning, reducing Attack Success Rate (ASR) from **100.0% to 0.0%**. Added sub-millisecond SHA-256 response caching and graceful degradation during upstream LLM outages.
