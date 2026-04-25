import streamlit as st
import requests
import time
import uuid
from typing import List, Dict, Any

# Set premium page config
st.set_page_config(
    page_title="MJ AI Document Explorer", 
    page_icon="🌌", 
    layout="centered"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# --- Per-user session ID (persisted in URL query params to survive refresh) ---
query_params = st.query_params
if "session_id" in query_params:
    # Restore session ID from URL on refresh
    st.session_state.session_id = query_params["session_id"]
elif "session_id" not in st.session_state:
    # First visit — generate a new session ID and put it in the URL
    st.session_state.session_id = str(uuid.uuid4())
    st.query_params["session_id"] = st.session_state.session_id

SESSION_HEADERS = {"X-Session-Id": st.session_state.session_id}

# --- Load chat history from backend on first run (e.g. after refresh) ---
if "messages" not in st.session_state:
    try:
        resp = requests.get(f"{BACKEND_URL}/history/load", headers=SESSION_HEADERS, timeout=3)
        if resp.status_code == 200:
            st.session_state.messages = resp.json().get("messages", [])
        else:
            st.session_state.messages = []
    except Exception:
        st.session_state.messages = []

def _save_history():
    """Save current chat messages to backend (best-effort)."""
    try:
        requests.post(
            f"{BACKEND_URL}/history/save",
            json={"messages": st.session_state.messages},
            headers=SESSION_HEADERS,
            timeout=3,
        )
    except Exception:
        pass

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

# --- Header row: title on the left, clear button on the right ---
header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown('<h1 class="premium-title">✨ MJ AI Document Explorer</h1>', unsafe_allow_html=True)
with header_right:
    st.write("")  # vertical spacer to align with title
    if st.button("🗑️ Clear", help="Clear chat and end session"):
        st.session_state.confirm_clear = True

# --- Confirmation dialog ---
if st.session_state.get("confirm_clear", False):
    st.warning("⚠️ Are you sure? This will delete your uploaded documents and chat history.")
    confirm_col1, confirm_col2 = st.columns(2)
    with confirm_col1:
        if st.button("✅ Yes", use_container_width=True):
            try:
                requests.post(f"{BACKEND_URL}/clear", headers=SESSION_HEADERS)
            except Exception:
                pass
            st.session_state.messages = []
            st.session_state.confirm_clear = False
            st.session_state.session_ended = True
            st.rerun()
    with confirm_col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.confirm_clear = False
            st.rerun()

# --- Session ended screen ---
if st.session_state.get("session_ended", False):
    import streamlit.components.v1 as components
    st.success("✅ Session cleared successfully. All uploaded documents and chat history have been deleted.")
    st.info("You can safely close this tab now.")
    # Attempt to close the browser tab via JavaScript
    components.html(
        """
        <script>
            // Try to close the tab — works if it was opened via JS or as a popup
            window.close();
        </script>
        """,
        height=0,
    )
    if st.button("💬 Start New Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id
        st.session_state.session_ended = False
        st.session_state.messages = []
        st.rerun()
    st.stop()  # Prevent the rest of the page from rendering

st.markdown('<p class="subtitle">Upload your PDF securely and interact seamlessly with its knowledge.</p>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    if st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files, headers=SESSION_HEADERS)
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(f"Error: {response.text}")

# Render chat history
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
            response = requests.get(f"{BACKEND_URL}/ask", params={"q": prompt}, headers=SESSION_HEADERS)
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
    
    # Persist chat history to backend after each exchange
    _save_history()
