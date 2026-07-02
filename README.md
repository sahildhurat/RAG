# Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Selected Mutual Funds (Stocks)
Based on the selected inputs, the assistant covers the following 10 mutual funds (stocks):

1. **[Parag Parikh Long Term Value Fund Direct Growth](https://groww.in/mutual-funds/parag-parikh-long-term-value-fund-direct-growth)**
2. **[Axis Silver FoF Direct Growth](https://groww.in/mutual-funds/axis-silver-fof-direct-growth)**
3. **[UTI Silver ETF FoF Direct Growth](https://groww.in/mutual-funds/uti-silver-etf-fof-direct-growth)**
4. **[HDFC Defence Fund Direct Growth](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)**
5. **[UTI Gold ETF FoF Direct Growth](https://groww.in/mutual-funds/uti-gold-etf-fof-direct-growth)**
6. **[Quantum Gold ETF FoF Direct Growth](https://groww.in/mutual-funds/quantum-gold-etf-fof-direct-growth)**
7. **[SBI PSU Fund Direct Growth](https://groww.in/mutual-funds/sbi-psu-fund-direct-growth)**
8. **[LIC MF Infrastructure Fund Direct Growth](https://groww.in/mutual-funds/lic-mf-infrastructure-fund-direct-growth)**
9. **[PGIM India Emerging Markets Equity FoF Direct Growth](https://groww.in/mutual-funds/pgim-india-emerging-markets-equity-fof-direct-growth)**
10. **[UTI Nifty 500 Value 50 Index Fund Direct Growth](https://groww.in/mutual-funds/uti-nifty-500-value-50-index-fund-direct-growth)**

### Corpus Definition (Official Sources)
*To strictly adhere to the facts-only constraint, the system ingests data exclusively from the official AMC websites for each of the 10 funds above, including their Scheme Information Documents (SIDs), Key Information Memorandums (KIMs), and monthly factsheets.*

#### Regulatory & General Reference Guidelines
- **AMFI Investor Corner:** [AMFI India Resource Center](https://www.amfiindia.com/investor-corner)
- **SEBI Mutual Funds Guidelines:** [SEBI Mutual Fund Section](https://www.sebi.gov.in/)

---

## Architecture Overview (RAG Approach)
The assistant uses a lightweight Retrieval-Augmented Generation (RAG) architecture:
1. **Data Ingestion:** Download the official SID, KIM, and Factsheet PDFs from the provided URLs. Parse and chunk the text using document loaders.
2. **Embeddings:** Convert the text chunks into high-dimensional vectors using an embedding model (e.g., `text-embedding-ada-002`).
3. **Vector Store:** Store these embeddings in a local or cloud vector database (like FAISS, ChromaDB, or Pinecone) to allow for fast semantic similarity searches.
4. **Retrieval:** When a user asks a query, embed the query and retrieve the top-K most relevant chunks from the vector store.
5. **Generation (LLM):** Pass the retrieved context to a Large Language Model with a strict system prompt. The prompt ensures the LLM answers purely based on the provided context, outputs a maximum of 3 sentences, includes the source link, appends the updated date, and politely refuses any advisory or opinion-based questions.

## Setup Instructions (Placeholder)
1. **Clone the Repository:** `git clone <repository_url>`
2. **Install Dependencies:** `pip install -r requirements.txt` (Ensure you have Streamlit, Langchain, and a VectorDB client installed).
3. **Set Environment Variables:** Create a `.env` file and add necessary API keys (e.g., `OPENAI_API_KEY`).
4. **Ingest Data:** Run the ingestion script to process the PDFs and populate the vector store: `python ingest.py`
5. **Run the App:** Launch the minimal UI using Streamlit: `streamlit run app.py`

## Known Limitations
- **Stale Data:** Factsheets are updated monthly, and SIDs/KIMs periodically. The corpus needs manual or automated scheduled refreshes; otherwise, data like AUM, expense ratios, or NAV will be outdated.
- **Corpus Boundaries:** The assistant cannot answer questions regarding schemes outside of the 4 selected funds.
- **Overly Cautious Refusals:** The system prompt might accidentally block valid factual queries if the user's wording closely resembles a request for advice (e.g., "Is the expense ratio good?").

## Disclaimer Snippet
> **Facts-only. No investment advice.**
