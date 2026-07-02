import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.llm_engine import answer_query

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="Requires GROQ_API_KEY")
def test_e2e_factual_query():
    query = "What is the exit load for Axis Silver Fund?"
    response = answer_query(query)
    
    # Verify the response is not empty
    assert len(response) > 10
    
    # Verify length constraint (<= 3 sentences usually, roughly checking length or periods)
    sentences = [s for s in response.split('.') if s.strip()]
    assert len(sentences) <= 5 # allowing 5 max for edge cases and formatting
    
    # Verify citation is present
    assert "Source:" in response
    assert "https://groww.in" in response
    
    # Verify footer is present
    assert "Last updated from sources:" in response

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="Requires GROQ_API_KEY")
def test_e2e_refusal_query():
    query = "Is Parag Parikh a good investment?"
    response = answer_query(query)
    
    # Verify refusal logic kicked in
    assert "amfiindia.com" in response.lower()
    assert "facts-only" in response.lower()
