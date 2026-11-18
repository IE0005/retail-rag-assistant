"""Chunk the knowledge base markdown docs and build a persistent Chroma vector store.

Run this once after generating store profiles (scripts/build_store_profiles.py),
and again any time a knowledge-base document changes.

    python ingest.py
"""
from pathlib import Path

import chromadb

ROOT = Path(__file__).parent
DOCS_DIR = ROOT / "knowledge_base" / "docs"
DB_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "retail_knowledge_base"


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split a markdown document into chunks along its top-level (##) sections.

    Each chunk is prefixed with the document's H1 title so it stays
    understandable on its own -- a chunk is what the retriever actually
    returns, without the rest of the document around it for context.
    """
    lines = text.splitlines()
    title = lines[0].lstrip("#").strip() if lines and lines[0].startswith("#") else source

    sections: list[list[str]] = [[]]
    for line in lines[1:]:
        if line.startswith("## "):
            sections.append([line])
        else:
            sections[-1].append(line)

    chunks = []
    for section_lines in sections:
        body = "\n".join(section_lines).strip()
        if not body:
            continue
        section_title = section_lines[0].lstrip("#").strip() if section_lines[0].startswith("##") else "(intro)"
        chunks.append(
            {
                "text": f"# {title}\n\n{body}",
                "source": source,
                "title": title,
                "section": section_title,
            }
        )
    return chunks


def load_all_docs() -> list[dict]:
    chunks = []
    for path in sorted(DOCS_DIR.rglob("*.md")):
        text = path.read_text()
        rel = str(path.relative_to(DOCS_DIR))
        chunks.extend(chunk_markdown(text, rel))
    return chunks


def main():
    chunks = load_all_docs()
    n_docs = len({c["source"] for c in chunks})
    print(f"Loaded {len(chunks)} chunks from {n_docs} documents")

    client = chromadb.PersistentClient(
        path=str(DB_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[f"{c['source']}::{i}" for i, c in enumerate(chunks)],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "title": c["title"], "section": c["section"]} for c in chunks],
    )
    print(f"Ingested {collection.count()} chunks into Chroma at {DB_DIR}")


if __name__ == "__main__":
    main()
