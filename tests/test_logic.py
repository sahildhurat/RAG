import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import scrub_pii
from src.llm_engine import detect_fund

def test_scrub_pii():
    text1 = "My PAN is ABCDE1234F."
    assert scrub_pii(text1) == "My PAN is [REDACTED_PAN]."
    
    text2 = "Aadhaar: 1234 5678 9012"
    assert scrub_pii(text2) == "Aadhaar: [REDACTED_AADHAAR]"
    
    text3 = "Account 1234567890123"
    assert scrub_pii(text3) == "Account [REDACTED_ACCOUNT]"
    
    text_clean = "What is the exit load?"
    assert scrub_pii(text_clean) == "What is the exit load?"

def test_detect_fund():
    assert detect_fund("axis silver") == "Axis Silver Fof Direct Growth"
    assert detect_fund("parag parikh flexi cap") == "Parag Parikh Long Term Value Fund Direct Growth"
    assert detect_fund("what about sbi psu?") == "Sbi Psu Fund Direct Growth"
    assert detect_fund("random query") is None
