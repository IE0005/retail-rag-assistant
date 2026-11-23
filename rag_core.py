"""Retrieval-augmented generation core: Chroma retrieval + Claude generation.

Retrieval and generation are deliberately kept as separate, inspectable
steps (retrieve() then answer_question()) rather than one opaque call, so
a caller -- or the Streamlit UI -- can show exactly what was retrieved
before the model ever sees it.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
import chromadb

try:
    import fcntl  # Mac/Linux only, which includes Streamlit Community Cloud
except ImportError:
    fcntl = None

ROOT = Path(__file__).parent
LOCK_PATH = ROOT / ".kb_build.lock"
DB_DIR = ROOT / "chroma_db"
STORE_PROFILES_DIR = ROOT / "knowledge_base" / "docs" / "store_profiles"
COLLECTION_NAME = "retail_knowledge_base"

MODEL = os.environ.get("RAG_MODEL", "claude-opus-5")
MAX_TOKENS = 2048
TOP_K = 5

STORE_PATTERN = re.compile(r"\bstore\s*#?\s*(\d{1,2})\b", re.IGNORECASE)
STORE_PROFILE_CHUNKS = 4  # a profile splits into intro + 3 "##" sections

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

    Streamlit reruns the script per session, so several runs can hit a cold
    start at once. They'd race on the model download and on ingest.py's
    delete/recreate of the collection, so only one run builds; the rest wait
    on the lock, then find the index already built and skip.
    """
    with open(LOCK_PATH, "w") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
        _build_if_needed()


def _build_if_needed():
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


def _to_chunks(results: dict) -> list:
    return [
        RetrievedChunk(
            text=text,
            source=meta.get("source", "unknown"),
            section=meta.get("section", ""),
            distance=dist,
        )
        for text, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]


def retrieve(query: str, k: int = TOP_K) -> list:
    """Return the most relevant knowledge-base chunks for a query.

    Plain vector search can't tell "Store 20" from "Store 22" -- embeddings
    treat the numbers as nearly identical -- so a question about a specific
    store would fill its top-k with other stores' profiles and miss the one
    asked about. When the query names a store, pull that store's profile
    chunks directly by metadata, and drop other stores' profiles from the
    similarity results so they can't crowd out or mislead the answer.
    """
    collection = _get_collection()
    similar = _to_chunks(collection.query(query_texts=[query], n_results=k))

    store_ids = sorted({int(n) for n in STORE_PATTERN.findall(query)})
    if not store_ids:
        return similar

    wanted = {f"store_profiles/store_{n:02d}.md" for n in store_ids}
    store_chunks = []
    for source in sorted(wanted):
        found = collection.query(
            query_texts=[query],
            n_results=STORE_PROFILE_CHUNKS,
            where={"source": source},
        )
        store_chunks.extend(_to_chunks(found))

    general = [
        c for c in similar if not c.source.startswith("store_profiles/") or c.source in wanted
    ]
    seen = {(c.source, c.section) for c in store_chunks}
    return store_chunks + [c for c in general if (c.source, c.section) not in seen]


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
