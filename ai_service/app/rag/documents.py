"""Document loading and chunking for the RAG pipeline."""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A chunk of documentation with metadata."""

    text: str
    source: str
    title: str
    section: str
    chunk_index: int


def load_documents(docs_dir: str) -> list[dict]:
    """Load all markdown files from the docs directory.

    Returns:
        List of dicts with keys: text, source, title.
    """
    documents = []
    if not os.path.isdir(docs_dir):
        logger.warning("Docs directory not found: %s", docs_dir)
        return documents

    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        # Derive title from first heading or filename
        title = filename.replace(".md", "").replace("_", " ").title()
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break
        documents.append({"text": text, "source": filename, "title": title})
        logger.info("Loaded document: %s (%d chars)", filename, len(text))

    return documents


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
) -> list[str]:
    """Split text into overlapping chunks.

    Tries to split on paragraph boundaries first, falls back to
    character-level splitting.

    Args:
        text: The full document text.
        chunk_size: Target chunk size in characters.
        overlap: Overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    # Split on double-newlines (paragraphs) first
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # If the paragraph itself is larger than chunk_size, split it
            if len(para) > chunk_size:
                words = para.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= chunk_size:
                        current = (current + " " + word).strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = word
            else:
                current = para

    if current:
        chunks.append(current)

    # Apply overlap: prepend the tail of the previous chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + " " + chunks[i])
        chunks = overlapped

    return chunks


def chunk_documents(documents: list[dict], chunk_size: int = 600, overlap: int = 100) -> list[DocumentChunk]:
    """Chunk all documents and return DocumentChunk objects with metadata.

    Args:
        documents: Output of load_documents().
        chunk_size: Target chunk size in characters.
        overlap: Overlap between consecutive chunks.

    Returns:
        List of DocumentChunk objects.
    """
    all_chunks = []
    for doc in documents:
        # Detect current section from headings
        sections = _extract_sections(doc["text"])
        text_chunks = chunk_text(doc["text"], chunk_size, overlap)
        for i, chunk_text_str in enumerate(text_chunks):
            # Find which section this chunk belongs to
            section = _find_section(chunk_text_str, sections) or doc["title"]
            all_chunks.append(
                DocumentChunk(
                    text=chunk_text_str,
                    source=doc["source"],
                    title=doc["title"],
                    section=section,
                    chunk_index=i,
                )
            )
    logger.info("Created %d chunks from %d documents", len(all_chunks), len(documents))
    return all_chunks


def _extract_sections(text: str) -> list[tuple[int, str]]:
    """Extract (position, heading) pairs from markdown text."""
    sections = []
    for i, line in enumerate(text.split("\n")):
        stripped = line.strip()
        if stripped.startswith("## "):
            sections.append((i, stripped.lstrip("# ").strip()))
        elif stripped.startswith("# "):
            sections.append((i, stripped.lstrip("# ").strip()))
    return sections


def _find_section(chunk: str, sections: list[tuple[int, str]]) -> str | None:
    """Find the most likely section heading for a chunk."""
    for _, heading in reversed(sections):
        if heading.lower() in chunk.lower():
            return heading
    return sections[0][1] if sections else None
