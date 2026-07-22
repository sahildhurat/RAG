import logging
import json
from langchain_community.document_loaders import WebBaseLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
import sys
import os

# Add parent directory to path to import vector_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# The 10 specific mutual fund URLs on Groww
FUNDS_URLS = [
    "https://groww.in/mutual-funds/parag-parikh-long-term-value-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-silver-fof-direct-growth",
    "https://groww.in/mutual-funds/uti-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-gold-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/quantum-gold-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/sbi-psu-fund-direct-growth",
    "https://groww.in/mutual-funds/lic-mf-infrastructure-fund-direct-growth",
    "https://groww.in/mutual-funds/pgim-india-emerging-markets-equity-fof-direct-growth",
    "https://groww.in/mutual-funds/uti-nifty-500-value-50-index-fund-direct-growth"
]

import re
from bs4 import BeautifulSoup

# --- Noise patterns to remove from scraped Groww pages ---
# These are Groww website navigation, footer, and unrelated stock/futures listings
NOISE_PATTERNS = [
    # Groww navigation menu items
    r'StocksInvest in Stocks.*?Brokerage and charges on GrowwBlog',
    # Footer: Stock market links, indices, futures, options
    r'(?:Top Gainers Stocks|Top Losers Stocks|Most Traded Stocks).*$',
    r'Share MarketIndices.*$',
    r'(?:NIFTY 50NIFTY Midcap|NIFTY Bank Options).*$',
    r'(?:MF Screener|Debt Mutual Funds|Best Multicap).*$',
    r'(?:Groww Arbitrage Fund|Groww ELSS).*$',
    r'(?:SIP Calculator|Brokerage Calculator).*$',
    r'(?:What is IPO\?).*$',
    r'(?:NSEBSEMCXTerms).*$',
    r'Vaishnavi Tech Park.*$',
    # Copyright and version
    r'© 2016-\d{4} Groww\..*$',
    # Product links
    r'PRODUCTSStocks.*?AMCPMS',
    r'Contact UsDownload the App.*$',
]

def clean_scraped_text(raw_text):
    """
    Cleans the raw scraped text from Groww pages by:
    1. Removing website navigation, footer, and unrelated stock/futures/options listings.
    2. Adding spaces between concatenated words (e.g., 'exitLoad' -> 'exit Load').
    3. Normalizing whitespace.
    """
    text = raw_text
    
    # Apply noise removal patterns
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Add space before capital letters that follow lowercase (fixes concatenated words)
    # e.g., "Exit LoadA fee" -> "Exit Load A fee"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Add space around common delimiters that are missing spaces
    text = re.sub(r'(\d)(₹)', r'\1 \2', text)  # "1000₹" -> "1000 ₹"
    text = re.sub(r'(₹)([\d])', r'\1\2', text)   # keep "₹5,000" together
    
    # Normalize multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove very short remaining text (likely noise artifacts)
    if len(text) < 100:
        return ""
    
    return text

def load_and_process_urls(urls):
    logger.info(f"Starting ingestion for {len(urls)} URLs...")
    docs = []
    
    for url in urls:
        try:
            logger.info(f"Loading {url}")
            loader = WebBaseLoader(url)
            page_docs = loader.load()
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            for doc in page_docs:
                # Clean the scraped text to remove Groww navigation/footer noise
                cleaned_content = clean_scraped_text(doc.page_content)
                if cleaned_content:
                    doc.page_content = cleaned_content
                    doc.metadata['source'] = url
                    doc.metadata['last_updated'] = current_date
                    # Extract fund name from URL for metadata filtering
                    fund_slug = url.split('/')[-1]
                    doc.metadata['fund_name'] = fund_slug.replace('-', ' ').title()
                    docs.append(doc)
                else:
                    logger.warning(f"Skipping {url} - no meaningful content after cleaning.")
        except Exception as e:
            logger.error(f"Error loading {url}: {e}")
            
    logger.info(f"Successfully loaded {len(docs)} cleaned document pages.")
    
    # Split text into chunks - smaller chunks for better retrieval precision
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    
    logger.info("Splitting documents into chunks...")
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Generated {len(chunks)} chunks.")
    
    return chunks

def load_and_process_pdfs(directory="data/"):
    if not os.path.exists(directory):
        logger.info(f"Directory {directory} does not exist. Skipping PDF ingestion.")
        return []
        
    logger.info(f"Starting PDF ingestion from {directory}...")
    try:
        loader = PyPDFDirectoryLoader(directory)
        docs = loader.load()
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        for doc in docs:
            # PyPDFLoader usually sets 'source' to the file path automatically. 
            # We'll just add the last_updated date.
            doc.metadata['last_updated'] = current_date
            
        logger.info(f"Successfully loaded {len(docs)} PDF pages.")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        logger.info("Splitting PDF documents into chunks...")
        chunks = text_splitter.split_documents(docs)
        logger.info(f"Generated {len(chunks)} PDF chunks.")
        
        return chunks
    except Exception as e:
        logger.error(f"Error loading PDFs from {directory}: {e}")
        return []

def save_to_files(chunks, output_dir="ingested_data"):
    """
    Saves the scraped and chunked data to reviewable files.
    - One .txt file per fund (raw content grouped by source URL)
    - One chunks_summary.json with all chunks and their metadata
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Group chunks by source URL and save one file per fund
    from collections import defaultdict
    grouped = defaultdict(list)
    for chunk in chunks:
        source = chunk.metadata.get('source', 'unknown')
        grouped[source].append(chunk)
    
    for source_url, source_chunks in grouped.items():
        # Create a safe filename from the URL
        fund_name = source_url.split('/')[-1] if '/' in source_url else source_url
        fund_name = fund_name.replace('.', '_')[:80]  # limit length
        filepath = os.path.join(output_dir, f"{fund_name}.txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Source: {source_url}\n")
            f.write(f"Total Chunks: {len(source_chunks)}\n")
            f.write(f"Last Updated: {source_chunks[0].metadata.get('last_updated', 'N/A')}\n")
            f.write("=" * 80 + "\n\n")
            for i, chunk in enumerate(source_chunks):
                f.write(f"--- Chunk {i+1} ---\n")
                f.write(chunk.page_content)
                f.write("\n\n")
        
        logger.info(f"Saved {len(source_chunks)} chunks to {filepath}")
    
    # 2. Save a JSON summary of all chunks with metadata
    summary_path = os.path.join(output_dir, "chunks_summary.json")
    summary = []
    for i, chunk in enumerate(chunks):
        summary.append({
            "chunk_id": i,
            "source": chunk.metadata.get('source', 'unknown'),
            "last_updated": chunk.metadata.get('last_updated', 'N/A'),
            "content_length": len(chunk.page_content),
            "content_preview": chunk.page_content[:200]
        })
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved chunks summary to {summary_path}")

def ingest_to_db():
    url_chunks = load_and_process_urls(FUNDS_URLS)
    pdf_chunks = load_and_process_pdfs()
    
    chunks = url_chunks + pdf_chunks
    
    if not chunks:
        logger.warning("No data to ingest. Exiting.")
        return
    
    # Save to reviewable files
    save_to_files(chunks)
        
    logger.info("Connecting to Vector Store...")
    vectorstore = get_vector_store()
    
    # Wipe stale embeddings so only the latest scrape is searchable.
    # Without this, daily runs pile up duplicate chunks with older dates,
    # and the retriever may surface outdated information.
    logger.info("Clearing old data from Vector Store...")
    vectorstore.delete_collection()
    vectorstore = get_vector_store()  # re-create the empty collection
    
    logger.info("Adding chunks to Vector Store (this may take a while)...")
    vectorstore.add_documents(chunks)
    logger.info("Ingestion complete!")

if __name__ == "__main__":
    ingest_to_db()
