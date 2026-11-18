"""Retrieval-augmented generation core: Chroma retrieval + Claude generation.

Retrieval and generation are deliberately kept as separate, inspectable
steps (retrieve() then answer_question()) rather than one opaque call, so
a caller -- or the Streamlit UI -- can show exactly what was retrieved
before the model ever sees it.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
import chromadb

ROOT = Path(__file__).parent
DB_DIR = ROOT / "chroma_db"
STORE_PROFILES_DIR = ROOT / "knowledge_base" / "docs" / "store_profiles"
COLLECTION_NAME = "retail_knowledge_base"

MODEL = os.environ.get("RAG_MODEL", "claude-opus-5")
MAX_TOKENS = 2048
TOP_K = 5

SYSTEM_PROMPT = """You are a retail operations knowledge assistant. You answer questions using
ONLY the knowledge base excerpts provided to you in each message -- never from
general knowledge, even if you happen to know something related.

Rules:
- Ground every claim in the provided excerpts. Cite the source document for
  each fact using the format (Source: <filename>).
- If the excerpts don't contain enough information to answer, say so plainly
  instead of guessing or filling in with general knowledge.
- If excerpts conflict, point out the conflict rather than silently picking
  one.
- Keep answers concise and direct."""


@dataclass
class RetrievedChunk:
    text: str
    source: str
    section: str
    distance: float


@dataclass
class RagAnswer:
    answer: str
    retrieved: list = field(default_factory=list)


def ensure_knowledge_base_built():
    """Build the store-profile docs and vector index on first run, if missing.

    Streamlit Community Cloud only runs `pip install -r requirements.txt`
    then the main file -- it won't run build_store_profiles.py or ingest.py
    for us, so the app has to be able to bootstrap its own index on a cold
    start rather than assuming someone ran those scripts by hand first.
    """
    if not STORE_PROFILES_DIR.exists() or not any(STORE_PROFILES_DIR.glob("*.md")):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_store_profiles.py")], check=True
        )

    needs_ingest = not DB_DIR.exists()
    if not needs_ingest:
        try:
            needs_ingest = _get_collection().count() == 0
        except Exception:
            needs_ingest = True
    if needs_ingest:
        subprocess.run([sys.executable, str(ROOT / "ingest.py")], check=True)


def _get_collection():
    client = chromadb.PersistentClient(
        path=str(DB_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    return client.get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = TOP_K) -> list:
    """Return the top-k most relevant knowledge-base chunks for a query."""
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=k)

    chunks = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    for text, meta, dist in zip(docs, metas, dists):
        chunks.append(
            RetrievedChunk(
                text=text,
                source=meta.get("source", "unknown"),
                section=meta.get("section", ""),
                distance=dist,
            )
        )
    return chunks


def _build_context_block(chunks: list) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Excerpt {i} — Source: {chunk.source}]\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


def _get_client(api_key: str = None) -> anthropic.Anthropic:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not key:
        raise RuntimeError(
            "No Anthropic API key provided. Pass one in (e.g. from the Streamlit sidebar), "
            "or set the ANTHROPIC_API_KEY environment variable for local development."
        )
    return anthropic.Anthropic(api_key=key)


def answer_question(query: str, api_key: str = None, k: int = TOP_K) -> RagAnswer:
    """Retrieve relevant knowledge-base chunks, then ask Claude to answer
    grounded only in those chunks. Returns both the answer and the retrieved
    chunks so a caller can show what the answer was actually based on.
    """
    chunks = retrieve(query, k=k)
    context_block = _build_context_block(chunks)

    client = _get_client(api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Knowledge base excerpts:\n\n{context_block}\n\n---\n\nQuestion: {query}",
            }
        ],
    )

    if response.stop_reason == "refusal":
        answer = "I'm not able to help with that request."
    else:
        answer = "".join(block.text for block in response.content if block.type == "text")

    return RagAnswer(answer=answer, retrieved=chunks)
