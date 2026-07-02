from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from tenacity import retry, stop_after_attempt, wait_exponential
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.vector_store import get_retriever

# Define the strict system prompt
SYSTEM_PROMPT = """You are a facts-only mutual fund FAQ assistant.
Your goal is to answer questions strictly using the provided context.

CRITICAL RULES:
1. Limit your response to a maximum of 3 sentences.
2. You MUST include exactly one citation link at the end of your response based on the context's source URL. 
   Format it as: "Source: <url>"
3. Include this exact footer on a new line at the very end of your response: "Last updated from sources: <date>" (Use the date from the context).
4. If the user asks for investment advice (e.g. "Should I invest?", "Which is better?"), or opinions, you MUST politely refuse.
   Instead say: "I am a facts-only assistant and cannot provide investment advice. For guidance, please visit https://www.amfiindia.com/investor-corner"
5. If the user asks about performance or returns, DO NOT state numbers. Instead say: "Please refer to the official factsheet for performance metrics. Source: <url>"
6. If the answer is not contained in the provided context, say "I do not have this information." Do not hallucinate.

System Knowledge (You ALWAYS know these facts):
- You have information on the following 10 mutual funds:
  1. Parag Parikh Long Term Value Fund
  2. Axis Silver FoF
  3. UTI Silver ETF FoF
  4. HDFC Defence Fund
  5. UTI Gold ETF FoF
  6. Quantum Gold ETF FoF
  7. SBI PSU Fund
  8. LIC MF Infrastructure Fund
  9. PGIM India Emerging Markets Equity FoF
  10. UTI Nifty 500 Value 50 Index Fund

Context:
{context}
"""

FUND_MAPPING = {
    "parag parikh": "Parag Parikh Long Term Value Fund Direct Growth",
    "axis silver": "Axis Silver Fof Direct Growth",
    "uti silver": "Uti Silver Etf Fof Direct Growth",
    "hdfc defence": "Hdfc Defence Fund Direct Growth",
    "hdfc defense": "Hdfc Defence Fund Direct Growth",
    "uti gold": "Uti Gold Etf Fof Direct Growth",
    "quantum gold": "Quantum Gold Etf Fof Direct Growth",
    "sbi psu": "Sbi Psu Fund Direct Growth",
    "sbi public sector": "Sbi Psu Fund Direct Growth",
    "lic": "Lic Mf Infrastructure Fund Direct Growth",
    "infrastructure": "Lic Mf Infrastructure Fund Direct Growth",
    "pgim": "Pgim India Emerging Markets Equity Fof Direct Growth",
    "emerging market": "Pgim India Emerging Markets Equity Fof Direct Growth",
    "uti nifty 500": "Uti Nifty 500 Value 50 Index Fund Direct Growth",
    "value 50": "Uti Nifty 500 Value 50 Index Fund Direct Growth"
}

def detect_fund(query: str):
    query_lower = query.lower()
    for keyword, full_name in FUND_MAPPING.items():
        if keyword in query_lower:
            return full_name
    return None

def format_docs(docs):
    formatted_chunks = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown URL')
        date = doc.metadata.get('last_updated', 'Unknown Date')
        fund = doc.metadata.get('fund_name', 'Unknown Fund')
        formatted_chunks.append(f"Content: {doc.page_content}\n[Metadata - Fund: {fund}, Source: {source}, Date: {date}]")
    return "\n\n---\n\n".join(formatted_chunks)

def _answer_query_internal(query: str) -> str:
    # 1. Detect if the user is asking about a specific fund
    fund_name = detect_fund(query)
    
    # 2. Configure MMR Search
    search_kwargs = {"k": 5, "fetch_k": 20}
    
    # 3. Apply Hard Metadata Filter if fund detected
    if fund_name:
        search_kwargs["filter"] = {"fund_name": fund_name}
        
    retriever = get_retriever(search_type="mmr", search_kwargs=search_kwargs)
    
    # 4. Initialize LLM (using robust 70b model, with max_retries at LangChain level as well)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=3)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}")
    ])
    
    # 5. Build and invoke chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(query)

# Apply exponential backoff to handle Groq rate limits (429 Too Many Requests)
# E.g. wait 2^x * 1 second between each retry, up to 10 seconds, max 5 attempts
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def answer_query(query: str) -> str:
    return _answer_query_internal(query)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Test query
    response = answer_query("What is the exit load for Axis Silver Fund?")
    print(response)
