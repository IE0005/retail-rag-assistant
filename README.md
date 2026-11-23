# Retail Knowledge Base RAG Assistant

A retrieval-augmented generation (RAG) chat assistant that answers retail
operations questions by retrieving relevant excerpts from a local knowledge
base, then asking Claude to answer grounded *only* in those excerpts —
with every answer showing exactly which sources it came from.

> The knowledge-base documents (policies, glossaries) are synthesized
> reference material written for this project, modeled on typical retail
> operations practice — not real corporate policy. The store performance
> profiles, however, are generated directly from real historical sales
> data (the same [Walmart Recruiting Store Sales Forecasting
> dataset](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)
> used in this project's companion repos).

## 🚀 Try it live

**[retail-rag-assistant-jfamb2rmsdrpba5q7wu4ph.streamlit.app](https://retail-rag-assistant-jfamb2rmsdrpba5q7wu4ph.streamlit.app)**

Ask it something like *"Why was Random Forest chosen over Extra Trees?"* or
*"How does Store 20 perform during holidays?"* and see which knowledge-base
excerpts it retrieved before answering.

This deploy uses a bring-your-own-key pattern — paste your own [Anthropic
API key](https://console.anthropic.com) into the sidebar to chat. Nothing
is stored or logged; it's only used for your requests in that browser
session.

## Architecture

```
knowledge_base/docs/*.md  ──┐
                             ├──▶ ingest.py ──▶ chroma_db/ (persistent vector store)
scripts/build_store_profiles.py ──┘                 │
                                                      ▼
                                    rag_core.retrieve(query)
                                                      │
                                                      ▼
                                    rag_core.answer_question(query)
                                     (retrieved chunks + query → Claude)
                                                      │
                                                      ▼
                                              rag_app.py (Streamlit UI)
```

1. **Chunking** (`ingest.py`) — each markdown document is split along its
   `##` section headers (not fixed-length windows), so every chunk stays a
   coherent, self-contained unit rather than an arbitrary mid-sentence
   slice. Each chunk is prefixed with its parent document's title, since a
   retrieved chunk won't have the rest of the document around it for
   context.
2. **Embedding + storage** — chunks are embedded with Chroma's default
   local embedding model (`all-MiniLM-L6-v2`, run via ONNX — no GPU, no
   API key, no cost) and stored in a persistent [Chroma](https://www.trychroma.com/)
   vector store on disk.
3. **Retrieval** (`rag_core.retrieve`) — embeds the user's question with
   the same model and returns the top-k nearest chunks by vector distance.
   Dense embeddings can't tell identifiers apart ("Store 20" and "Store 22"
   embed almost identically), so when a question names a store, that
   store's profile is pulled directly with a metadata filter and other
   stores' profiles are dropped from the similarity results.
4. **Grounded generation** (`rag_core.answer_question`) — the retrieved
   chunks are placed in the prompt, and Claude is instructed to answer
   using *only* those excerpts, cite the source document for every claim,
   and say plainly when the knowledge base doesn't contain the answer
   rather than filling in from general knowledge.

## Project layout

- `knowledge_base/docs/` — hand-written retail operations glossaries and
  policy references (markdown events, holiday impact, store formats,
  economic indicators, inventory replenishment, forecasting methodology,
  anomaly detection methods)
- `knowledge_base/docs/store_profiles/` — one auto-generated profile per
  store, computed from real sales data (see below)
- `data/` — the raw sales dataset (`train.csv`, `features.csv`, `stores.csv`)
- `scripts/build_store_profiles.py` — computes per-store sales stats
  (trend, holiday lift, top/bottom departments) and writes them as
  markdown documents
- `ingest.py` — chunks all knowledge-base documents and builds the
  persistent Chroma vector store
- `rag_core.py` — retrieval + Claude generation logic
- `rag_app.py` — the Streamlit chat UI, showing retrieved sources per turn

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run rag_app.py
```

The first launch automatically generates the store-profile documents and
builds the vector index if they don't exist yet (you'll see a "Setting up
knowledge base (first run only)..." spinner) — no manual steps needed.
This also means the app bootstraps itself correctly on a fresh Streamlit
Community Cloud deploy, which only runs `pip install -r requirements.txt`
and then the main file, with no way to run a separate setup script first.

The agent needs an Anthropic API key, entered directly in the app's
sidebar — this is a bring-your-own-key design, so no key is baked into the
deployment and hosting it costs nothing. For local dev convenience, you
can pre-fill that sidebar field by exporting `ANTHROPIC_API_KEY` before
launching, or adding it to `.streamlit/secrets.toml` (gitignored, never
committed).

By default the assistant uses `claude-opus-5`; override with the
`RAG_MODEL` env var (e.g. `RAG_MODEL=claude-sonnet-5`) for a
cheaper/faster model.

If you change a knowledge-base document or the underlying data, re-run
`python3 scripts/build_store_profiles.py && python3 ingest.py` manually —
the auto-bootstrap only runs when the index is missing entirely, not on
every change.

## Deploying to Streamlit Community Cloud

1. Push this directory to a GitHub repo.
2. Go to https://share.streamlit.io, sign in, and click "New app".
3. Point it at the repo, branch, and `rag_app.py` as the main file.
4. Deploy. Community Cloud installs from `requirements.txt` automatically,
   then the app builds its own knowledge base and index on first load (see
   above). If the build fails on a very new default Python version, set it
   to `3.10` under **Advanced settings** before deploying.
5. No Secrets configuration needed — it's bring-your-own-key, so each
   visitor supplies their own Anthropic API key in the sidebar.
