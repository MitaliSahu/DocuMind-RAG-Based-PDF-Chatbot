# PDF RAG Chatbot using Ollama

## Features
- Upload multiple PDFs
- Ask questions about PDFs
- ChromaDB vector database
- Page number citations
- Chat memory
- Ollama (Llama 3.2)

## Prerequisites

Install Python 3.12+

Install Ollama:
https://ollama.com

Pull the models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Installation

Clone the repository:

```bash
git clone <your-github-url>
cd pdf-rag-ollama
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Ollama:

```bash
ollama serve
```

Run the application:

```bash
streamlit run app.py
```