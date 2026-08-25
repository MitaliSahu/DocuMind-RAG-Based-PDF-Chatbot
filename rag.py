import os
import shutil
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import HumanMessage

from pdf_loader import load_pdf_documents
from chat_memory import add_message, get_history

from config import (
    CHROMA_DB,
    EMBEDDING_MODEL,
    LLM_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
)

# Models
embedding = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0
)

# Split Documents
def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_documents(documents)

    return chunks

# Create Vector DB
def create_vectorstore(chunks):

    if os.path.exists(CHROMA_DB):

        shutil.rmtree(CHROMA_DB)
    # Force Chroma to release any previous database locks
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    
    # Your original code starting on line 51:
    vectorstore = Chroma.from_documents(
        documents=chunks,
        # ... the rest of your parameters (embedding, persist_directory, etc.)
    )
    Chroma.from_documents(

        documents=chunks,

        embedding=embedding,

        persist_directory=CHROMA_DB

    )

# Process PDFs
def process_uploaded_files(files):

    docs = load_pdf_documents(files)

    chunks = split_documents(docs)

    create_vectorstore(chunks)

# Load DB
def get_vectorstore():

    return Chroma(

        persist_directory=CHROMA_DB,

        embedding_function=embedding

    )
    
# Semantic Search
def retrieve(question):

    db = get_vectorstore()

    docs = db.similarity_search_with_score(

        question,

        k=TOP_K

    )

    return docs

# Prompt
def build_prompt(question, docs):

    context = ""

    for doc, score in docs:

        context += doc.page_content

        context += "\n\n"

    history = get_history()

    prompt = f"""
You are an intelligent assistant.

Answer ONLY using the supplied context.

If the answer cannot be found inside the documents,
reply:

"I couldn't find that information in the uploaded PDFs."

Conversation History:

{history}

Context:

{context}

Question:

{question}

Answer:
"""

    return prompt


# ===================================
# Answer Question
# ===================================

def answer_question(question):

    retrieved = retrieve(question)

    prompt = build_prompt(question, retrieved)

    response = llm.invoke(

        [HumanMessage(content=prompt)]

    )

    answer = response.content

    add_message(question, answer)

    sources = []

    for doc, score in retrieved:

        sources.append({

            "page": doc.metadata.get("page", 0) + 1,

            "file": doc.metadata.get(

                "filename",

                "Unknown"

            ),

            "score": round(score, 3),

            "text": doc.page_content[:500]

        })

    return answer, sources