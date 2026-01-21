# indexing/document_loader.py

from pathlib import Path
import fitz  # PyMuPDF

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "docs" / "pdf_raw"

def load_documents(data_dir: Path = DATA_DIR):
    documents = []

    for file_path in data_dir.rglob("*"):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Handle PDFs: Treat every PAGE as a separate "document"
        if file_path.suffix.lower() == ".pdf":
            with fitz.open(file_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    page_text = page.get_text()
                    
                    # Only add if the page actually has text
                    if page_text.strip():
                        documents.append({
                            "doc_id": file_path.stem,  # Filename without extension
                            "text": page_text,         # Text of just this page
                            "source": str(file_path),
                            "page_num": page_num       # <--- Capture Page Number
                        })
        
        # Handle TXT/MD: Treat the whole file as one document
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            if text.strip():
                documents.append({
                    "doc_id": file_path.stem,
                    "text": text,
                    "source": str(file_path),
                    "page_num": 1  # Default to page 1 for non-PDFs
                })

    return documents


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    print(f"Loaded {len(docs)} documents (pages)")

    if docs:
        print("\nSample text from first page:\n")
        print(f"File: {docs[0]['doc_id']}, Page: {docs[0]['page_num']}")
        print(docs[0]["text"][:500])
    else:
        print("No documents found. Check data directory path.")