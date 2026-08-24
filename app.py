import streamlit as st
import os
from pathlib import Path

from rag import process_uploaded_files
from rag import answer_question
# -----------------------------
# 1. Authentication System
# -----------------------------
def check_password():
    """Returns `True` if the user provides the correct credentials."""

    def password_entered():
        # Hardcoded credentials for demonstration. 
        # (For a real production app, store these in a database or Streamlit Secrets)
        if st.session_state["username"] == "admin" and st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            # Clear credentials from session state for security
            del st.session_state["password"]  
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # If already authenticated, allow them to proceed
    if st.session_state.get("password_correct", False):
        # Optional: Add a logout button to the sidebar later
        return True

    # If not authenticated, render the login form
    st.title("🔒 ResQMind AI - Staff Login")
    
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    
    st.button("Login", on_click=password_entered)

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Incorrect username or password")
    
    return False

# -----------------------------
# 2. Authorization Gate
# -----------------------------
# This stops the script from running the RAG app until the login passes
if not check_password():
    st.stop() 


# ==========================================
# 3. YOUR ORIGINAL APP CODE GOES BELOW
# ==========================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide"
)

# ... (Paste the rest of your session states, sidebar, and chat logic here) ...
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectorstore_ready" not in st.session_state:
    st.session_state.vectorstore_ready = False

if "documents" not in st.session_state:
    st.session_state.documents = []

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.title("📚DocuMind")

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Create Knowledge Base"):

        if uploaded_files:

            saved_files = []

            for pdf in uploaded_files:

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    pdf.name
                )

                with open(filepath, "wb") as f:
                    f.write(pdf.read())

                saved_files.append(filepath)

            with st.spinner("Processing PDFs..."):

                process_uploaded_files(saved_files)

            st.session_state.vectorstore_ready = True
            st.session_state.documents = saved_files

            st.success("Knowledge Base Created")

        else:

            st.warning("Please upload at least one PDF.")

    st.markdown("---")

    st.subheader("Indexed PDFs")

    if len(st.session_state.documents) == 0:

        st.info("No PDFs uploaded.")

    else:

        for pdf in st.session_state.documents:

            st.write("📄", Path(pdf).name)

    st.markdown("---")

    if st.button("Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()

# -----------------------------
# Main Page
# -----------------------------

st.title("📄 PDF Question Answering")

st.caption(
    "Ask questions about your uploaded documents using Ollama."
)

st.markdown("---")

# -----------------------------
# Show Previous Messages
# -----------------------------

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if "sources" in message:

                with st.expander("Sources"):

                    for src in message["sources"]:

                        st.markdown(
                            f"""
### 📄 {src['file']}

**Page:** {src['page']}

**Similarity Score:** {src['score']}

---

{src['text']}
"""
                        )

# -----------------------------
# Chat Input
# -----------------------------

question = st.chat_input(
    "Ask something about the uploaded PDFs..."
)

if question:

    if not st.session_state.vectorstore_ready:

        st.warning(
            "Please upload and process PDFs first."
        )

        st.stop()

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching documents..."):

            answer, sources = answer_question(question)

        st.markdown(answer)

        with st.expander("Sources"):

            for src in sources:

                st.markdown(
                    f"""
### 📄 {src['file']}

**Page:** {src['page']}

**Similarity Score:** {src['score']}

---

{src['text']}
"""
                )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )