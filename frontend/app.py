import streamlit as st
import requests
import time
from typing import List, Dict, Any

# Set premium page config
st.set_page_config(
    page_title="MJ AI Document Explorer", 
    page_icon="🌌", 
    layout="centered"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Inject Custom CSS for Premium Design
st.markdown("""
<style>
    /* Import modern Google font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Vibrant Gradient Title */
    .premium-title {
        background: linear-gradient(135deg, #00F0FF 0%, #8A2BE2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.2rem;
        padding-bottom: 5px;
        margin-bottom: 0;
    }
    
    .subtitle {
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Glassmorphism buttons and neat animations */
    .stButton>button {
        border-radius: 12px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #8A2BE2 0%, #0062ff 100%);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(138, 43, 226, 0.5);
        color: white;
    }
    
    /* Source Exander Styling */
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        color: #00F0FF;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="premium-title">✨ MJ AI Document Explorer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your PDF securely and interact seamlessly with its knowledge.</p>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(f"Error: {response.text}")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("Sources"):
                for i, source in enumerate(message["sources"]):
                    st.write(f"**Source {i+1}:**")
                    st.write(source["content"][:200] + "...")
                    if "page" in source["metadata"]:
                        st.write(f"Page: {source['metadata']['page']}")

if prompt := st.chat_input("Ask a question about the uploaded documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.get(f"{BACKEND_URL}/ask", params={"q": prompt})
            if response.status_code == 200:
                data = response.json()
                st.markdown(data["answer"])
                sources = data["sources"]
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": data["answer"],
                    "sources": sources
                })
            else:
                st.error(f"Error: {response.text}")