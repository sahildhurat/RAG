import streamlit as st
from dotenv import load_dotenv
from src.utils import scrub_pii
from src.llm_engine import answer_query

load_dotenv()

st.set_page_config(page_title="Mutual Fund FAQ Assistant", page_icon="📈", layout="centered")

# --- UI Setup ---
st.title("📈 Mutual Fund FAQ Assistant")
st.markdown("> **Disclaimer:** Facts-only. No investment advice.")

st.markdown("""
Welcome to the facts-only Mutual Fund FAQ Assistant. You can ask factual questions regarding our 10 tracked mutual fund schemes.
""")

st.subheader("Example Questions:")
st.markdown("""
- *What is the exit load for Parag Parikh Long Term Value Fund?*
- *What is the minimum SIP amount for Axis Silver FoF?*
- *How can I download the capital gains report?*
""")

st.divider()

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a factual question about the mutual funds..."):
    # 1. Scrub PII
    safe_prompt = scrub_pii(prompt)
    
    # 2. Display user message in chat message container
    st.chat_message("user").markdown(safe_prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": safe_prompt})

    # 3. Generate and display assistant response
    with st.spinner("Retrieving facts..."):
        try:
            response = answer_query(safe_prompt)
        except Exception as e:
            response = f"An error occurred: {e}. Please ensure GROQ_API_KEY is configured."
            
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
