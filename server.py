from mcp.server.fastmcp import FastMCP
from app.qa_index import QAIndex
from app.postman_loader import load_postman_collection
from app.google_llm import generate_answer

# Initialize MCP server
mcp = FastMCP(
    name="api-docs-mcp-server",
    host="127.0.0.1",
    port=3333
)


qa = QAIndex()

@mcp.tool()
def load_postman_collection_tool(file_bytes: str):
    """
    Load and index a Postman collection JSON.
    file_bytes: Postman collection JSON as string
    """
    chunks = load_postman_collection(file_bytes.encode())
    added = 0

    for chunk in chunks:
        qa.add_document(
            text=chunk["text"],
            doc_id=f"postman::{chunk['metadata']['method']}::{chunk['metadata']['endpoint']}"
        )
        added += 1

    return {
        "status": "ok",
        "indexed_endpoints": added
    }


@mcp.tool()
def query_docs(question: str, top_k: int = 3):
    """
    Retrieve relevant documentation chunks.
    """
    results = qa.search(question, top_k=top_k)
    return [
        {
            "score": score,
            "endpoint": meta.get("doc_id"),
            "text": meta.get("chunk_text")
        }
        for score, meta in results
    ]


@mcp.tool()
def ask_llm(question: str, top_k: int = 3):
    """
    Answer questions using retrieved context.
    """
    results = qa.search(question, top_k=top_k)

    if not results:
        return {"answer": "I cannot find this information in the documentation."}

    context = "\n\n---\n\n".join(meta["chunk_text"] for _, meta in results)
    answer = generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {"endpoint": meta["doc_id"], "score": score}
            for score, meta in results
        ]
    }


if __name__ == "__main__":
    mcp.run()