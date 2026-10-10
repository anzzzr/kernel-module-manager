"""Tests for evaluation metric functions."""

import pytest

from eval.metrics import (
    compute_category_match,
    compute_false_positive,
    compute_groundedness,
    compute_keyword_coverage,
    compute_mrr,
    compute_recall_at_k,
)


def test_recall_at_k():
    retrieved = ["docA.md", "docB.md", "docC.md"]
    gold = ["docB.md", "docD.md"]

    assert compute_recall_at_k(retrieved, gold, k=1) == 0.0
    assert compute_recall_at_k(retrieved, gold, k=2) == 0.5
    assert compute_recall_at_k(retrieved, gold, k=3) == 0.5
    assert compute_recall_at_k(retrieved, [], k=3) == 1.0


def test_mrr():
    gold = ["docC.md", "docD.md"]
    assert compute_mrr(["docA.md", "docB.md", "docC.md"], gold) == pytest.approx(1.0 / 3.0)
    assert compute_mrr(["docC.md", "docA.md"], gold) == 1.0
    assert compute_mrr(["docA.md", "docB.md"], gold) == 0.0
    assert compute_mrr([], gold) == 0.0


def test_category_match():
    assert compute_category_match(
        "NVIDIA kernel module vermagic string mismatch with current kernel",
        "vermagic/kernel version mismatch"
    )
    assert compute_category_match(
        "Module cannot be loaded: Direct firmware load for iwlwifi failed",
        "missing firmware"
    )
    assert compute_category_match(
        "Module is loaded and operating normally; no errors detected",
        "healthy module"
    )
    assert not compute_category_match(
        "Fatal error loading module: file corrupted",
        "healthy module"
    )


def test_keyword_coverage():
    text = "The driver failed due to a missing firmware file iwlwifi.ucode with error -2"
    keywords = ["firmware", "iwlwifi", "error -2", "recompile"]
    assert compute_keyword_coverage(text, keywords) == 0.75
    assert compute_keyword_coverage(text, []) == 1.0


def test_groundedness():
    corpus = ["module_loading.md", "nvidia_troubleshooting.md", "modprobe.md"]
    refs = ["module_loading.md - Vermagic", "nvidia_troubleshooting.md#sec2"]
    assert compute_groundedness(refs, corpus) == 1.0

    hallucinated_refs = ["module_loading.md", "random_unreal_doc.md"]
    assert compute_groundedness(hallucinated_refs, corpus) == 0.5
    assert compute_groundedness([], corpus) == 1.0


def test_false_positive():
    assert not compute_false_positive("healthy module", "Module is healthy and operating normally.")
    assert compute_false_positive("healthy module", "Critical failure: module driver crashed.")
    assert not compute_false_positive("missing firmware", "Critical failure: firmware missing.")
