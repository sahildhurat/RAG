from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our RAG modules
from src.llm_engine import answer_query
from src.utils import scrub_pii

# Load environment variables (e.g. GROQ_API_KEY)
load_dotenv()

app = FastAPI(
    title="Mutual Fund FAQ API",
    description="Facts-only API for querying Mutual Fund details.",
    version="1.0.0"
)

# Enable CORS for local testing with the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (update in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Scrub PII from the incoming query
        safe_query = scrub_pii(request.query)
        
        # 2. Get the response from the LLM engine
        result = answer_query(safe_query)
        
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
