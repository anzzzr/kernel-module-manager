"""Evaluation metric functions for kernel module diagnostic benchmarking."""

import re
from typing import Sequence


def compute_recall_at_k(retrieved_sources: Sequence[str], gold_sources: Sequence[str], k: int) -> float:
    """Compute Recall@k for document retrieval.

    Recall@k = (Number of relevant gold sources in top-k) / (Total number of gold sources)
    """
    if not gold_sources:
        return 1.0

    top_k = retrieved_sources[:k]
    matched = sum(1 for g in gold_sources if g in top_k)
    return matched / float(len(gold_sources))


def compute_mrr(retrieved_sources: Sequence[str], gold_sources: Sequence[str]) -> float:
    """Compute Mean Reciprocal Rank (MRR) for document retrieval.

    Returns the reciprocal rank of the first relevant gold source retrieved (1 / rank),
    or 0.0 if no relevant source is found.
    """
    if not gold_sources:
        return 1.0

    for idx, src in enumerate(retrieved_sources, start=1):
        if src in gold_sources:
            return 1.0 / float(idx)
    return 0.0


def compute_category_match(predicted_text: str, gold_category: str) -> bool:
    """Check if the predicted diagnosis text semantically matches the gold category."""
    pred_lower = predicted_text.lower()
    cat_lower = gold_category.lower()

    # Category matching rules based on domain keywords
    category_patterns = {
        "vermagic/kernel version mismatch": [
            r"vermagic", r"version magic", r"version mismatch", r"module_layout", r"disagrees about version"
        ],
        "missing dependency": [
            r"missing depend", r"dependency", r"depends on", r"unknown symbol.*dependency"
        ],
        "secure boot signature rejection": [
            r"secure boot", r"unsigned module", r"key was rejected", r"lockdown", r"mok", r"pkcs#7"
        ],
        "missing firmware": [
            r"firmware", r"missing.*firmware", r"direct firmware load", r"\.ucode", r"\.bin"
        ],
        "blacklisted module": [
            r"blacklist", r"blacklisted", r"modprobe\.d"
        ],
        "module already loaded/in use": [
            r"in use", r"already loaded", r"refcount", r"cannot unload", r"used by"
        ],
        "unknown symbol / abi mismatch": [
            r"unknown symbol", r"abi mismatch", r"symbol version", r"disagrees about version"
        ],
        "dkms build failure": [
            r"dkms", r"build failure", r"compilation failed", r"kernel headers", r"make\.log"
        ],
        "healthy module": [
            r"healthy", r"normal", r"no fault", r"no issue", r"loaded and operating", r"no action required"
        ],
    }

    patterns = category_patterns.get(cat_lower, [re.escape(cat_lower)])
    for pat in patterns:
        if re.search(pat, pred_lower):
            return True
    return False


def compute_keyword_coverage(text: str, gold_keywords: Sequence[str]) -> float:
    """Calculate the fraction of gold keywords/phrases present in the generated text."""
    if not gold_keywords:
        return 1.0

    text_lower = text.lower()
    matched = 0
    for kw in gold_keywords:
        if kw.lower() in text_lower:
            matched += 1
    return matched / float(len(gold_keywords))


def compute_groundedness(doc_references: Sequence[str], corpus_filenames: Sequence[str]) -> float:
    """Calculate the citation groundedness score (fraction of citations existing in corpus).

    A score of 1.0 means zero hallucinated doc citations.
    If no citations were generated, returns 1.0 if not expected, or 0.0.
    """
    if not doc_references:
        return 1.0

    valid_files = set(f.lower() for f in corpus_filenames)
    valid_count = 0

    for ref in doc_references:
        ref_lower = ref.lower()
        # Check if any known document file is mentioned in the reference string
        is_valid = any(
            doc_file in ref_lower or doc_file.replace(".md", "") in ref_lower
            for doc_file in valid_files
        )
        if is_valid:
            valid_count += 1

    return valid_count / float(len(doc_references))


def compute_false_positive(category: str, predicted_diagnosis: str) -> bool:
    """Returns True if a healthy module was falsely classified as having a defect."""
    if category.lower() != "healthy module":
        return False

    pred_lower = predicted_diagnosis.lower()
    benign_phrases = [
        "healthy", "normal", "no fault", "no error", "no issue",
        "functioning correctly", "operating normally", "no action"
    ]
    is_benign = any(bp in pred_lower for bp in benign_phrases)
    return not is_benign
