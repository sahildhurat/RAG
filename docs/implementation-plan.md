# Implementation Plan: Mutual Fund FAQ Assistant (RAG)

The goal is to build a complete, end-to-end facts-only FAQ assistant for mutual fund schemes using a Retrieval-Augmented Generation (RAG) architecture. This plan translates the requirements from `ProblemStatement.md` and the design from `architecture.md` into concrete, actionable development steps and a clear codebase structure.

## User Review Required

> [!IMPORTANT]
> **Technology Stack Lock-in**: The primary LLM provider is set to **Groq (llama-3.3-70b-versatile)**, and the embedding model is set to a **HuggingFace BGE model**. The Vector DB defaults to **ChromaDB** (for local, easy setup).

## Data Ingestion Strategy
- We will use a hybrid approach: the system will directly scrape the Groww/AMC URLs **and** parse any manually downloaded PDFs placed in a local `/data` directory.

## PII Scrubbing
- We will rely on a basic Regex-based approach for scrubbing PAN and Account numbers to keep the project lightweight.

## Proposed Changes

We will create a modular Python codebase.

### Phase 1: Project Configuration & Setup

#### [NEW] [requirements.txt](file:///d:/RAG/requirements.txt)
- Will include dependencies: `streamlit`, `langchain`, `langchain-groq`, `langchain-huggingface`, `chromadb`, `pypdf`, `python-dotenv`.

#### [NEW] [.env.example](file:///d:/RAG/.env.example)
- Template for environment variables (e.g., `GROQ_API_KEY`).

---

### Phase 2: Data Ingestion Layer

#### Phase 2A: Vector Store Initialization
**Goal:** Set up ChromaDB and the HuggingFace BGE embedding model so all later phases have a working storage target.

##### [NEW] [src/vector_store.py](file:///d:/RAG/src/vector_store.py)
- Initialize the HuggingFace `BAAI/bge-base-en-v1.5` embedding model (768-dim vectors).
- Create the local ChromaDB instance (persisted to `./chroma_db`).
- Expose a `get_retriever(k)` function for downstream use by the LLM engine.

**Verification:** Run a quick script to confirm the embedding model loads and a test string can be embedded without errors.

---

#### Phase 2B: URL Scraping & Text Cleaning
**Goal:** Connect to the 10 Groww mutual fund URLs, extract page content, and **strip out website noise** before chunking.

##### [MODIFY] [src/ingest.py](file:///d:/RAG/src/ingest.py) — `load_and_process_urls()` & `clean_scraped_text()`

**Data Quality Issues Identified:**
- Groww pages contain heavy navigation menus ("Invest in Stocks, ETFs, IPOs..."), footer links (stock names, futures, options, indices, calculators), and promotional content that made up ~50% of raw scraped text.
- Text is concatenated without spaces (e.g., `ExitLoadA fee` instead of `Exit Load A fee`), breaking semantic meaning for embeddings.

**Cleaning Pipeline (applied before chunking):**
1. **Regex noise removal** — 13 targeted patterns strip out Groww navigation, footer, stock/futures/options listings, calculator links, copyright notices, and product menus.
2. **CamelCase splitting** — Regex inserts spaces between lowercase→uppercase transitions (e.g., `ExitLoadA` → `Exit Load A`).
3. **Whitespace normalization** — Collapses multiple spaces/newlines into single spaces.
4. **Empty page guard** — Pages with <100 chars after cleaning are skipped entirely.

**Metadata enrichment:**
- `source`: The Groww URL.
- `last_updated`: Current date.
- `fund_name`: Extracted from the URL slug (e.g., `Axis Silver Fof Direct Growth`).

**Verification:** Run the function in isolation and confirm:
- All 10 URLs return non-empty `Document` objects with meaningful text (no nav/footer junk).
- Metadata includes `source`, `last_updated`, and `fund_name`.

---

#### Phase 2C: Local PDF Ingestion
**Goal:** Parse any manually downloaded PDFs (SIDs, KIMs, Factsheets) placed in the `data/` directory.

##### [MODIFY] [src/ingest.py](file:///d:/RAG/src/ingest.py) — `load_and_process_pdfs()`
- Use `PyPDFDirectoryLoader` to recursively load all `.pdf` files from `data/`.
- Attach `last_updated` metadata to each page.
- Gracefully handle the case where the `data/` directory does not exist (skip with a log message, no crash).

**Verification:** Place a sample PDF in `data/`, run the function, and confirm the extracted text is readable and metadata is attached.

---

#### Phase 2D: Chunking, Embedding & Storage
**Goal:** Split all cleaned documents (from both 2B and 2C) into chunks optimized for factual retrieval, embed them, and persist in ChromaDB.

##### [MODIFY] [src/ingest.py](file:///d:/RAG/src/ingest.py) — `ingest_to_db()`

**Chunking Strategy (tuned after data analysis):**
- `RecursiveCharacterTextSplitter` with:
  - `chunk_size=800` (reduced from 1000 — smaller chunks improve retrieval precision for specific facts like expense ratio or exit load).
  - `chunk_overlap=150` (reduced from 200 — less overlap needed after noise removal).
  - `separators=["\n\n", "\n", ". ", ", ", " "]` — prioritizes splitting on sentence boundaries instead of mid-word.

**Embedding Model:** HuggingFace `BAAI/bge-base-en-v1.5` (768-dim vectors). Chosen for:
- Strong performance on financial/factual text retrieval.
- Lightweight enough to run locally on CPU without GPU.
- Fast inference (~45s for 154 chunks).

**Data Export:** All chunks are also saved to `ingested_data/` as reviewable `.txt` files (one per fund) and a `chunks_summary.json` for auditing.

**Results (after cleaning):**
| Metric | Before Cleaning | After Cleaning |
| :--- | :---: | :---: |
| Total chunks | 208 | 154 |
| Noise chunks removed | — | 54 (26%) |
| Avg chunks per fund | 20.8 | 15.4 |

**Verification:** After running `python -m src.ingest`, query ChromaDB with a known keyword (e.g., "exit load") and confirm relevant chunks are returned with correct metadata (`source`, `fund_name`, `last_updated`).

---

### Phase 3: Generation & Logic Layer

**Model Selection & Rate Limiting Context:**
We are using Groq's `llama-3.3-70b-versatile` model. Because this is a free-tier Groq API, we must handle strict rate limits:
- Requests per minute (RPM): 30
- Requests per day (RPD): 1,000
- Tokens per minute (TPM): 12,000
- Tokens per day (TPD): 100,000

To prevent crashes when users send messages too rapidly, we will implement exponential backoff/retry logic (e.g., using the `tenacity` library or LangChain's built-in retry mechanisms) on LLM calls.

**Data Quality Context:**
Because we have 10 different mutual funds, chunks across different funds look semantically identical (e.g., they all mention "Exit Load", "AUM", "Expense Ratio"). A basic vector search is highly likely to retrieve the exit load of Fund B when the user asks about Fund A.

**Updated Retrieval Strategy:**
1. **Metadata Pre-Filtering:** 
   - We will implement a router/extractor step before retrieval. It will detect if a specific fund name (e.g., "Parag Parikh", "Axis Silver") is mentioned in the query.
   - If a fund is detected, we will apply a strict `where` filter to ChromaDB based on the `fund_name` metadata we injected in Phase 2. This completely eliminates cross-fund hallucinations.
2. **MMR (Maximal Marginal Relevance):**
   - We will switch from basic similarity search to MMR (`search_type="mmr"`, `k=5`, `fetch_k=20`). This ensures we pull diverse chunks instead of 4 nearly identical chunks, giving the LLM broader context.

#### [MODIFY] [src/llm_engine.py](file:///d:/RAG/src/llm_engine.py)
- Update `get_qa_chain()` to include a simple fund-name extraction step (via regex or string matching against a known list of the 10 funds).
- Pass the extracted `fund_name` as a `filter` to the ChromaDB retriever.
- Update retriever configuration to use MMR.
- Defines the strict **System Prompt** enforcing the 3-sentence limit, exact citations, and refusal handling for investment advice.

#### [NEW] [src/utils.py](file:///d:/RAG/src/utils.py)
- Helper functions, including the Regex-based PII scrubber to sanitize inputs before sending them to the LLM.

---

### Phase 4: User Interface

#### [NEW] [app.py](file:///d:/RAG/app.py)
- The main Streamlit application.
- Implements the minimal UI: Welcome banner, disclaimer, example questions, and the chat interface.
- Wires the frontend to `llm_engine.py`.

## Verification Plan

### Automated Tests
- N/A for this rapid prototype phase, though unit tests for PII scrubbing (`pytest src/utils.py`) could be added if requested.

### Manual Verification
1. **Ingestion:** Run `python src/ingest.py` and verify that the local ChromaDB database is populated without errors.
2. **UI:** Run `streamlit run app.py` and verify the frontend loads correctly.
3. **Factual Queries:** Ask "What is the exit load for Parag Parikh Long Term Value Fund?" -> Verify response is <= 3 sentences, contains 1 citation, and the footer.
4. **Refusal Handling:** Ask "Is HDFC Defence Fund a good investment?" -> Verify the system refuses to answer and provides an AMFI/SEBI link.
5. **PII Handling:** Ask a query containing a fake PAN card number -> Verify the system scrubs it before processing.
