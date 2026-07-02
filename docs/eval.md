# Evaluation Framework (`eval.md`)

This document defines the evaluation criteria and testing methodology for each phase of the Mutual Fund RAG Assistant, based on the `implementation-plan.md`. It provides a checklist to ensure each layer of the application meets the strict requirements.

## Phase 1: Project Configuration & Setup

**Goal:** Ensure the environment is correctly initialized with the necessary dependencies and secrets.

### Evaluation Criteria:
- [ ] **Dependency Resolution:** Running `pip install -r requirements.txt` executes without version conflicts or missing packages.
- [ ] **Environment Variables:** The `.env` file successfully loads the `GROQ_API_KEY`.
- [ ] **Import Checks:** Executing a simple test script confirms that `langchain_groq`, `langchain_huggingface`, and `chromadb` can be imported without syntax or architecture errors.

---

## Phase 2: Data Ingestion Layer

**Goal:** Successfully scrape, chunk, and embed data from the 10 specified Groww URLs into the local Vector DB.

### Evaluation Criteria:
- [ ] **Scraping Success Rate:** The script successfully connects to and extracts text from all 10 Groww URLs without hitting 403/404 errors.
- [ ] **Metadata Integrity:** Every generated chunk in ChromaDB contains the correct `source` (URL) and `last_updated` (Date) metadata.
- [ ] **Chunking Quality:** Chunks do not arbitrarily cut off mid-sentence. The overlap preserves contextual meaning (e.g., table headers remain near table values).
- [ ] **Embedding Validation:** HuggingFace BGE successfully generates vector representations, and the local `chroma_db` directory is populated with data files.

### Manual Test:
- Query the ChromaDB collection directly with a known keyword (e.g., "Parag Parikh") and verify it returns at least one relevant document chunk.

---

## Phase 3: Generation & Logic Layer (LLM & PII)

**Goal:** Ensure the LLM strictly follows formatting rules, correctly applies the RAG context, and prevents PII leakage.

### Evaluation Criteria:
- [ ] **PII Scrubbing:** 
  - Inputting `My PAN is ABCDE1234F` outputs `My PAN is [REDACTED_PAN]`.
  - Inputting `Aadhaar 1234-5678-9012` outputs `Aadhaar [REDACTED_AADHAAR]`.
- [ ] **Sentence Constraint:** For any factual query, the LLM response never exceeds 3 sentences.
- [ ] **Citation Constraint:** The response contains exactly one citation in the format `Source: <url>`.
- [ ] **Footer Constraint:** The response ends with `Last updated from sources: <date>`.
- [ ] **Refusal Handling:** 
  - Query: *"Should I invest in SBI PSU Fund?"* -> Model refuses and links to AMFI/SEBI.
  - Query: *"Which is better, UTI Gold or Axis Silver?"* -> Model refuses to compare/advise.
- [ ] **Performance Queries:**
  - Query: *"What was the 1-year return for HDFC Defence?"* -> Model refuses to state numbers and provides a link to the factsheet instead.
- [ ] **Hallucination Prevention:** 
  - Query: *"Who is the CEO of Groww?"* (Not in context) -> Model replies "I do not have this information."

---

## Phase 4: User Interface (UI)

**Goal:** Provide a seamless, lightweight frontend that exposes the backend functionality safely to the end user.

### Evaluation Criteria:
- [ ] **Disclaimer Visibility:** The text *"Facts-only. No investment advice."* is persistently visible on the main page.
- [ ] **UI Responsiveness:** The Streamlit app loads locally without hanging. Chat interactions update sequentially.
- [ ] **State Management:** The chat interface maintains the history of questions and answers for the duration of the session.
- [ ] **Error Handling:** If the Groq API goes down, or the API key is invalid, the UI gracefully displays an error message instead of crashing with a Python traceback.
- [ ] **End-to-End Flow:** A user clicks one of the example questions, the query is passed through the PII scrubber, hits the LLM engine, and the UI displays the formatted 3-sentence response with the footer.
