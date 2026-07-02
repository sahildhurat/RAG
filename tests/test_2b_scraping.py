"""Phase 2B Verification: Test URL scraping in isolation."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest import load_and_process_urls, FUNDS_URLS

print(f"Attempting to scrape {len(FUNDS_URLS)} URLs...\n")

# We won't chunk yet — just test the raw document loading
from langchain_community.document_loaders import WebBaseLoader
from datetime import datetime

docs = []
for i, url in enumerate(FUNDS_URLS):
    try:
        loader = WebBaseLoader(url)
        page_docs = loader.load()
        current_date = datetime.now().strftime("%Y-%m-%d")
        for doc in page_docs:
            doc.metadata['source'] = url
            doc.metadata['last_updated'] = current_date
        docs.extend(page_docs)
        content_preview = page_docs[0].page_content[:200].replace('\n', ' ').strip()
        print(f"[{i+1}/10] OK - {url}")
        print(f"   Preview: {content_preview}")
        print(f"   Metadata: {page_docs[0].metadata}")
        print()
    except Exception as e:
        print(f"[{i+1}/10] FAILED - {url}")
        print(f"   Error: {e}")
        print()

print(f"\n--- SUMMARY ---")
print(f"Total documents loaded: {len(docs)}")
if len(docs) > 0:
    print("Phase 2B PASSED")
else:
    print("Phase 2B FAILED - No documents loaded!")
