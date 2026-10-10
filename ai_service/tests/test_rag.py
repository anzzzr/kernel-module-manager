"""Tests for the RAG pipeline: documents, chunking, store, and service."""

import os

import pytest
from kernel_diagnostic_ai.models import Evidence
from kernel_diagnostic_ai.rag.documents import chunk_documents, chunk_text, load_documents
from kernel_diagnostic_ai.services.rag_service import build_query


class TestLoadDocuments:
    def test_loads_from_docs_dir(self):
        """Verify documents are loaded from the project docs directory."""
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        if not os.path.isdir(docs_dir):
            pytest.skip("docs directory not found")
        docs = load_documents(docs_dir)
        assert len(docs) > 0
        for doc in docs:
            assert "text" in doc
            assert "source" in doc
            assert "title" in doc
            assert doc["text"]  # not empty

    def test_loads_expected_files(self):
        """Verify specific documentation files are present."""
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        if not os.path.isdir(docs_dir):
            pytest.skip("docs directory not found")
        docs = load_documents(docs_dir)
        sources = [d["source"] for d in docs]
        expected = ["kernel_modules.md", "modprobe.md", "common_errors.md"]
        for exp in expected:
            assert exp in sources, f"Missing expected doc: {exp}"

    def test_empty_dir(self, tmp_path):
        """Verify empty directory returns empty list."""
        docs = load_documents(str(tmp_path))
        assert docs == []

    def test_nonexistent_dir(self):
        """Verify nonexistent directory returns empty list."""
        docs = load_documents("/nonexistent/path")
        assert docs == []


class TestChunkText:
    def test_short_text_single_chunk(self):
        """Text shorter than chunk_size returns single chunk."""
        chunks = chunk_text("Short text", chunk_size=600)
        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_long_text_multiple_chunks(self):
        """Long text is split into multiple chunks."""
        text = "\n\n".join([f"Paragraph {i}. " * 20 for i in range(10)])
        chunks = chunk_text(text, chunk_size=300, overlap=50)
        assert len(chunks) > 1

    def test_chunks_not_empty(self):
        """All chunks should have content."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph with more text to fill."
        chunks = chunk_text(text, chunk_size=30, overlap=10)
        for chunk in chunks:
            assert len(chunk.strip()) > 0

    def test_overlap_present(self):
        """Consecutive chunks should have overlapping content."""
        text = "\n\n".join([f"Section {i} content here." for i in range(20)])
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        if len(chunks) >= 2:
            # The second chunk should start with end of first chunk
            # (due to overlap implementation)
            assert len(chunks[1]) > 20


class TestChunkDocuments:
    def test_chunks_have_metadata(self):
        """Verify chunk documents carry source metadata."""
        docs = [
            {"text": "# Test Doc\n\nParagraph one.\n\nParagraph two.", "source": "test.md", "title": "Test Doc"},
        ]
        chunks = chunk_documents(docs, chunk_size=600, overlap=0)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.source == "test.md"
            assert chunk.title == "Test Doc"
            assert chunk.chunk_index >= 0


class TestBuildQuery:
    def test_basic_query(self):
        """Verify query includes module name."""
        evidence = Evidence(module="nvidia", commands={"uname": "5.15.0"}, errors={})
        query = build_query(evidence)
        assert "nvidia" in query
        assert "5.15.0" in query

    def test_query_includes_errors(self):
        """Verify query includes error information."""
        evidence = Evidence(
            module="nvidia",
            commands={"uname": "5.15.0"},
            errors={"modinfo": "Module not found"},
        )
        query = build_query(evidence)
        assert "Module not found" in query

    def test_query_includes_modinfo_details(self):
        """Verify query extracts key modinfo fields."""
        evidence = Evidence(
            module="nvidia",
            commands={
                "uname": "5.15.0",
                "modinfo": "description: NVIDIA GPU driver\ndepends: drm\nvermagic: 5.15.0 SMP",
            },
            errors={},
        )
        query = build_query(evidence)
        assert "description:" in query.lower() or "depends:" in query.lower()


class TestRAGStoreIntegration:
    """Integration tests for ChromaDB store — only run if chromadb is importable."""

    def test_store_lifecycle(self, tmp_path):
        """Test init → populate → query cycle."""
        try:
            from kernel_diagnostic_ai.rag.documents import DocumentChunk
            from kernel_diagnostic_ai.rag.store import init_store, populate_store, query_store
        except ImportError:
            pytest.skip("chromadb or sentence-transformers not installed")

        # Init store in temp dir
        init_store(str(tmp_path / "chroma"))

        # Create test chunks
        chunks = [
            DocumentChunk(
                text="The NVIDIA kernel module requires matching kernel headers to compile.",
                source="nvidia.md",
                title="NVIDIA Troubleshooting",
                section="Kernel Headers",
                chunk_index=0,
            ),
            DocumentChunk(
                text="Use modprobe to load kernel modules with automatic dependency resolution.",
                source="modprobe.md",
                title="modprobe",
                section="Basic Usage",
                chunk_index=0,
            ),
            DocumentChunk(
                text="The loop module provides loopback block device support for mounting disk images.",
                source="misc.md",
                title="Misc Modules",
                section="loop",
                chunk_index=0,
            ),
        ]

        # Populate
        added = populate_store(chunks)
        assert added == 3

        # Query — should find nvidia-related content
        results = query_store("nvidia module loading error kernel headers", n_results=2)
        assert len(results) > 0
        # The nvidia chunk should be most relevant
        assert any("nvidia" in r["text"].lower() for r in results)

    def test_empty_store_query(self, tmp_path):
        """Query on empty store returns empty list."""
        try:
            from kernel_diagnostic_ai.rag.store import init_store, query_store
        except ImportError:
            pytest.skip("chromadb not installed")

        init_store(str(tmp_path / "chroma_empty"))
        results = query_store("test query")
        assert results == []
