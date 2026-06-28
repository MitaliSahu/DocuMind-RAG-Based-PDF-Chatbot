import streamlit as st
import os
from pathlib import Path

from rag import process_uploaded_files
from rag import answer_question

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="PDF RAG Chatbot",
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

    st.title("📚 PDF RAG Chatbot")

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