# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import time
from pathlib import Path

from indexing.indexing_pipeline import run_indexing
from generation.answer_generation import AnswerGenerator
from database.metadata_store import MetadataStore
from database.chat_store import ChatStore # <--- NEW

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = AnswerGenerator()
chat_store = ChatStore() # Initialize SQLite Store

# --- Data Models ---
class QueryRequest(BaseModel):
    query: str
    model: str = "qwen2.5:3b"
    session_id: str
    target_document: Optional[str] = None # <--- NEW

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    generation_time: float

class RenameRequest(BaseModel):
    title: str

# --- Routes ---

@app.get("/api/status")
def get_status():
    db = MetadataStore()
    try:
        db.cursor.execute("SELECT COUNT(*) as count FROM document_chunks")
        result = db.cursor.fetchone()
        count = result['count'] if result else 0
    except:
        count = 0
    finally:
        db.close()
    
    return {
        "status": "online",
        "indexed_chunks": count,
        "model": "Qwen 2.5 3B (Contextual)"
    }

@app.get("/api/documents")
def get_documents():
    upload_dir = Path("docs/pdf_raw")
    if not upload_dir.exists():
        return []
    
    files = []
    for f in upload_dir.iterdir():
        if f.is_file() and f.suffix.lower() in ['.pdf', '.txt', '.md']:
            stats = f.stat()
            files.append({
                "name": f.name,
                "size": f"{stats.st_size / 1024:.1f} KB",
                "date": time.strftime('%Y-%m-%d %H:%M', time.localtime(stats.st_mtime)),
                "timestamp": stats.st_mtime
            })
    return files

@app.delete("/api/documents/{filename}")
def delete_document(filename: str):
    file_path = Path("docs/pdf_raw") / filename
    if file_path.exists():
        os.remove(file_path)
        return {"message": "File deleted"}
    raise HTTPException(status_code=404, detail="File not found")

# --- CHAT HISTORY ROUTES ---

@app.get("/api/history")
def get_history():
    return chat_store.get_sessions()

@app.get("/api/history/{session_id}")
def get_session_messages(session_id: str):
    return chat_store.get_messages(session_id)

@app.post("/api/history")
def create_session(data: dict):
    chat_store.create_session(data['id'], data['title'], data['date'])
    return {"message": "Session created"}

@app.delete("/api/history/{session_id}")
def delete_session(session_id: str):
    chat_store.delete_session(session_id)
    return {"message": "Session deleted"}

@app.patch("/api/history/{session_id}")
def rename_session(session_id: str, req: RenameRequest):
    chat_store.update_session_title(session_id, req.title)
    return {"message": "Session renamed"}

# --- QUERY ROUTE ---

@app.post("/api/query", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    try:
        start_time = time.time()
        
        # 1. Save User Message
        chat_store.add_message(request.session_id, "user", request.query)
        
        # 2. Generate Answer (Pass target_document)
        result = generator.generate_answer(
            request.query, 
            model_name=request.model,
            target_document=request.target_document
        )
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        # 3. Save Bot Message
        chat_store.add_message(
            request.session_id, 
            "assistant", 
            result["answer"], 
            result["sources"], 
            duration
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "generation_time": duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    upload_dir = Path("docs/pdf_raw")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    for file in files:
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
        
    return {"message": f"Successfully uploaded {len(saved_files)} files", "files": saved_files}

@app.post("/api/reindex")
def trigger_indexing():
    try:
        run_indexing() 
        return {"message": "Indexing completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)