import os

from langchain_community.document_loaders import PyPDFLoader


def load_pdf_documents(pdf_files):
    """
    Load all uploaded PDF files.

    Adds filename metadata so it can be shown
    in the citation.
    """

    all_pages = []

    for pdf in pdf_files:

        loader = PyPDFLoader(pdf)

        pages = loader.load()

        filename = os.path.basename(pdf)

        for page in pages:
            page.metadata["filename"] = filename

        all_pages.extend(pages)

    return all_pages