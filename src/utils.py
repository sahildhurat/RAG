import re

def scrub_pii(text: str) -> str:
    """
    Scrubs sensitive Personal Identifiable Information (PII) from user queries.
    Specifically targets:
    - PAN Cards (Format: 5 letters, 4 numbers, 1 letter)
    - Aadhaar Numbers (Format: 12 digits, optional spaces/hyphens)
    - Account Numbers (General 9-18 digit numbers)
    """
    
    # 1. Scrub PAN Card (e.g., ABCDE1234F)
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
    text = re.sub(pan_pattern, '[REDACTED_PAN]', text, flags=re.IGNORECASE)
    
    # 2. Scrub Aadhaar (e.g., 1234-5678-9012 or 1234 5678 9012)
    aadhaar_pattern = r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
    text = re.sub(aadhaar_pattern, '[REDACTED_AADHAAR]', text)
    
    # 3. Scrub Account Numbers (9 to 18 digits)
    account_pattern = r'\b\d{9,18}\b'
    text = re.sub(account_pattern, '[REDACTED_ACCOUNT_NUMBER]', text)
    
    return text

if __name__ == "__main__":
    # Simple test
    test_str = "My PAN is ABCDE1234F and my account is 1234567890123. Aadhaar is 1234-5678-9012."
    print("Original:", test_str)
    print("Scrubbed:", scrub_pii(test_str))
