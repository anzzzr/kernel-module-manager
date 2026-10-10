# Interactive Terminal Demo & Verification Guide

This guide walks through reproducing and recording the live end-to-end diagnostic pipeline using `DEMO_MODE=true`.

In `DEMO_MODE`, the Go host daemon serves verified diagnostic fixtures (`eval/cases`) and simulates module management operations, allowing developers and reviewers to test the entire pipeline on macOS, Linux, or Windows without requiring root privileges or a Linux kernel.

---

## 1. Quick Start Demo (Single Command)

Run the included automated demonstration script:

```bash
chmod +x scripts/demo_run.sh
./scripts/demo_run.sh
```

### Verified Real Output:
```json
$ curl -s -X POST http://127.0.0.1:8080/module/nvidia/diagnose \
    -H 'Authorization: Bearer admin-secret-token'

{
    "module": "nvidia",
    "evidence": {
        "module": "nvidia",
        "commands": {
            "dmesg": "[  124.512014] nvidia: version magic '6.5.0-28-generic SMP preempt mod_unload modversions' should be '6.8.0-40-generic SMP preempt mod_unload modversions'\n[  124.512028] nvidia: disagrees about version of symbol module_layout",
            "journalctl": "systemd-modules-load[412]: Failed to insert module 'nvidia': Exec format error",
            "lsmod": "Module                  Size  Used by\nnvme                   61440  4\n",
            "modinfo": "filename:       /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko\nversion:        535.183.01\nvermagic:       6.5.0-28-generic SMP preempt mod_unload modversions\ndepends:        nvidia-modeset\n",
            "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko",
            "uname": "6.8.0-40-generic"
        },
        "errors": {
            "modprobe": "modprobe: ERROR: could not insert 'nvidia': Exec format error"
        }
    },
    "ai_analysis": {
        "diagnosis": "[DEMO] Diagnostic assessment for module 'nvidia'. Identified system telemetry state.",
        "possible_causes": [
            "Kernel vermagic / symbol mismatch"
        ],
        "recommendations": [
            "Ensure matching linux-headers package is installed",
            "Verify firmware files exist in /lib/firmware"
        ],
        "evidence_used": [
            "module: nvidia",
            "commands.uname",
            "commands.dmesg"
        ],
        "uncertainty": "low",
        "documentation_references": [
            "module_loading.md",
            "common_errors.md"
        ],
        "safety_flags": []
    },
    "rag_context_used": true,
    "safety_flags": [],
    "ai_status": "available"
}
```

---

## 2. Running Live in Docker Compose

You can launch both microservices in containers with zero external dependencies:

```bash
# 1. Start containers in DEMO_MODE
make up
# or: docker compose up -d

# 2. Check service health
curl http://localhost:8080/health
curl http://localhost:8001/health

# 3. Request diagnosis for canned error cases
# Case A: vermagic mismatch (nvidia)
curl -X POST http://localhost:8080/module/nvidia/diagnose \
     -H "Authorization: Bearer admin-secret-token"

# Case B: missing firmware (iwlwifi)
curl -X POST http://localhost:8080/module/iwlwifi/diagnose \
     -H "Authorization: Bearer admin-secret-token"

# Case C: blacklisted driver (nouveau)
curl -X POST http://localhost:8080/module/nouveau/diagnose \
     -H "Authorization: Bearer admin-secret-token"

# 4. Check real-time operational stats
curl http://localhost:8080/stats
curl http://localhost:8001/stats

# 5. Stop containers
make down
```

---

## 3. Recording a Terminal Cast / GIF

To record a reproducible demo session for documentation or GitHub Releases:

### Using asciinema:
```bash
# Install asciinema (macOS: brew install asciinema / Linux: apt install asciinema)
asciinema rec docs/demo.cast -c ./scripts/demo_run.sh
```

### Converting to GIF with agg:
```bash
# Install agg (asciinema gif generator: brew install agg / cargo install agg)
agg docs/demo.cast docs/demo.gif --cols 100 --rows 30 --theme monokai
```

---

## 4. Key Architectural Behaviors Demonstrated

1. **Request Propagation**: The Go daemon assigns an `X-Request-ID` and sends the sanitized telemetry to the Python AI service.
2. **Hybrid RAG Retrieval**: Python searches ChromaDB and BM25 index over the 26-doc corpus, injecting relevant kernel docs into context (`rag_context_used: true`).
3. **Safety Scanning**: The output safety filter scans generated recommendations before returning them to the client.
4. **Zero-Privilege Security**: All commands run without root privileges; privileged operations are refused unless explicitly permitted by policy.
