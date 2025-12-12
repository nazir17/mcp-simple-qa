import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.utils import extract_text_from_file_bytes
from app.qa_index import QAIndex
from typing import Optional
import uvicorn

app = FastAPI(title="Simple MCP-like QA server (extractive)")

# initialize global index
qa = QAIndex()

class QueryRequest(BaseModel):
    q: str
    top_k: Optional[int] = 3

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), doc_id: Optional[str] = None):
    data = await file.read()
    text = extract_text_from_file_bytes(file.filename, data)
    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail="No text extracted from file.")
    count = qa.add_document(text, doc_id=doc_id or file.filename)
    return {"status": "ok", "added_chunks": count, "doc_id": doc_id or file.filename}

@app.post("/query")
async def query(qr: QueryRequest):
    if not qr.q or qr.q.strip() == "":
        raise HTTPException(status_code=400, detail="Empty query.")
    results = qa.search(qr.q, top_k=qr.top_k)
    return {"query": qr.q, "results": [{"score": r[0], "text": r[1].get("chunk_text"), "doc_id": r[1].get("doc_id")} for r in results]}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
