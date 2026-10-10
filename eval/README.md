# Evaluation Dataset & Benchmark Suite

This directory contains the benchmark dataset and evaluation runner used to empirically measure the accuracy, retrieval efficiency, hallucination rate, and operational characteristics of the kernel module diagnosis system.

## 1. Dataset Breakdown

The benchmark suite consists of **46 realistic diagnostic cases** across 10 distinct failure and healthy modes:

| Category | Count | Failure Mechanism & Signature |
|:---|:---:|:---|
| **vermagic/kernel version mismatch** | 5 | Kernel version drift following OS update; `vermagic` string mismatch on `module_layout` |
| **missing dependency** | 5 | Dependent module uninstalled or not loaded; unresolved symbols (`err -2`) |
| **Secure Boot signature rejection** | 5 | UEFI Lockdown mode restricting unsigned third-party/DKMS binaries (`PKCS#7` key rejection) |
| **missing firmware** | 5 | Missing hardware blob under `/lib/firmware` with kernel ring buffer error `-2` (ENOENT) |
| **blacklisted module** | 5 | Administrative module blocking in `/etc/modprobe.d/*.conf` |
| **module already loaded/in use** | 5 | Cannot unload via `rmmod`; active refcounts held by mounted filesystems or dependent drivers |
| **unknown symbol / ABI mismatch** | 5 | Kernel ABI break or interface changes between minor point releases |
| **DKMS build failure** | 4 | Compilation failure during kernel headers build or GCC compiler mismatch |
| **healthy module (negative controls)** | 4 | Modules loaded and functioning normally; evaluated to check **false positive rates** |
| **noisy/irrelevant logs** | 3 | Real failures buried under unrelated kernel logs (disk timeouts, audio glitches, USB disconnects) |

---

## 2. Provenance & Transparency (Synthetic vs Adapted)

To maintain strict truthfulness:
- **Adapted Public Bug Reports**: Cases adapted from real-world Linux bug trackers (Ubuntu Launchpad, Debian BTS, OpenZFS GitHub issues, VirtualBox Bug Tracker, NVIDIA Developer Forums). In these cases, the original log structure and error signatures were preserved, with URLs cited directly in the case metadata (`source_reference`). No proprietary or copyrighted text is included.
- **Synthetic Ground Truth Cases**: Clean synthetic cases generated based on upstream Linux kernel documentation (`Documentation/kbuild/modules.rst`, `Documentation/security/secrets/kernel_lockdown.rst`).
- Every test case contains:
  - `id`: Unique identifier
  - `module`: Target kernel module
  - `evidence`: Exact JSON payload matching the Go backend diagnostic collector schema
  - `gold_root_cause_category`: Canonical failure category
  - `gold_keywords`: Domain-specific technical terms required for diagnostic validity
  - `gold_doc_sources`: Markdown documentation files containing the grounding explanation
  - `source_type`: Either `"adapted_public_bug"` or `"synthetic"`

---

## 3. Evaluation Modes

The benchmark suite (`eval/run_eval.py`) runs three distinct modes against the dataset:

1. **`no_rag` (Zero-Shot / Base LLM)**:
   - Direct LLM diagnostic call with diagnostic evidence only. No documentation is supplied in context.
   - Tests model pretraining knowledge without augmentation.
2. **`rag` (Vector RAG Pipeline)**:
   - Retrieves top-$k$ documentation chunks from ChromaDB embedded using `sentence-transformers/all-MiniLM-L6-v2`.
   - Augments prompt with retrieved documentation sections.
3. **`full_docs` (Full Context / Stuffed Baseline)**:
   - Injects the **entire documentation corpus** (~5,000 words / ~20KB) directly into the prompt context window.
   - Answers the key engineering question: *Does vector RAG beat full context when the entire corpus easily fits in a modern 128k context window?*

---

## 4. How to Run the Evaluation

### CI / Mock Mode (Deterministic & Free, No API Keys Needed)
```bash
python3 eval/run_eval.py --mode all --mock-llm
```

### Live LLM Evaluation (Requires API Key)
Set your provider API key (e.g. OpenAI or Groq) and execute:
```bash
export LLM_API_KEY="your-api-key"
export LLM_MODEL="gpt-4o-mini" # or llama-3.3-70b-versatile
python3 eval/run_eval.py --mode all
```

### Parameter Ablations (Chunk Sizes & Top-K)
```bash
python3 eval/run_eval.py --ablate --mock-llm
```
