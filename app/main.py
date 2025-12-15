import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.utils import extract_text_from_file_bytes
from app.qa_index import QAIndex
from typing import Optional
import uvicorn
from app.google_llm import generate_answer
from app.postman_loader import load_postman_collection

app = FastAPI(title="Simple MCP-like QA server (extractive)")

# initialize global index
qa = QAIndex()

class QueryRequest(BaseModel):
    q: str
    top_k: Optional[int] = 3

class AskLLMRequest(BaseModel):
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

@app.post("/ask_llm")
async def ask_llm(req: AskLLMRequest):
    if not req.q or req.q.strip() == "":
        raise HTTPException(status_code=400, detail="Empty question.")

    results = qa.search(req.q, top_k=req.top_k)

    if not results:
        return {
            "question": req.q,
            "answer": "I cannot find this information in the document.",
            "sources": []
        }

    context_blocks = []
    sources = []

    for score, meta in results:
        text = meta.get("chunk_text", "")
        context_blocks.append(text)
        sources.append({
            "doc_id": meta.get("doc_id"),
            "score": score
        })

    context = "\n\n---\n\n".join(context_blocks)

    answer = generate_answer(req.q, context)

    return {
        "question": req.q,
        "answer": answer,
        "sources": sources
    }

@app.post("/upload_postman")
async def upload_postman(file: UploadFile = File(...)):
    data = await file.read()

    try:
        api_chunks = load_postman_collection(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Postman JSON: {e}")

    if not api_chunks:
        raise HTTPException(status_code=400, detail="No API endpoints found")

    added = 0
    for chunk in api_chunks:
        qa.add_document(
            text=chunk["text"],
            doc_id=f"postman::{chunk['metadata']['method']}::{chunk['metadata']['endpoint']}"
        )
        added += 1

    print(chunk["text"])

    return {
        "status": "ok",
        "indexed_endpoints": added
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
