import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("src.api.answer_query")
def test_chat_endpoint(mock_answer_query):
    # Setup mock return value
    mock_answer_query.return_value = "Mocked LLM Response."
    
    response = client.post("/chat", json={"query": "Test query"})
    
    assert response.status_code == 200
    assert response.json() == {"response": "Mocked LLM Response."}
    mock_answer_query.assert_called_once_with("Test query")

@patch("src.api.answer_query")
def test_chat_endpoint_with_pii(mock_answer_query):
    mock_answer_query.return_value = "Mocked LLM Response."
    
    response = client.post("/chat", json={"query": "My PAN is ABCDE1234F"})
    
    assert response.status_code == 200
    # verify PII was scrubbed BEFORE being passed to answer_query
    mock_answer_query.assert_called_once_with("My PAN is [REDACTED_PAN]")
