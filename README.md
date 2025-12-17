MCP Server for API Q&A from Postman Collections

This project is a pure MCP (Model Context Protocol) server that allows users to ask natural-language questions about APIs using Postman collection files as the knowledge source.

It is designed to be tested and used via MCP-compatible clients, such as MCP Inspector, copilot and claude desktop.

✨ Key Features

📄 Load Postman collection JSON files

🔍 Index API endpoints using vector embeddings

🤖 Answer questions exclusively via Google Gemini LLM

🧩 MCP-native design using mcp-use

🧪 Tested via MCP Inspector and copilot


🏗️ Architecture Overview
Postman Collection (JSON)
        ↓
MCP Tool: load_postman_collection
        ↓
Vector Index (SentenceTransformers + FAISS)
        ↓
MCP Tool: ask_llm
        ↓
Google Gemini LLM
        ↓
Answer (grounded in API context)

📂 Project Structure
mcp-simple-qa/
│
├── server.py              # MCP server entry point
├── google_llm.py          # Google Gemini LLM wrapper
├── postman_loader.py      # Postman collection parser
├── qa_index.py            # Embeddings + FAISS index
├── requirements.txt       # Project dependencies
└── README.md

⚙️ Requirements

Python 3.9+

Linux / macOS / Windows

Google Generative AI API key

🔐 Environment Setup

Create a .env file in the project root:

GOOGLE_API_KEY=your_google_api_key_here

🐍 Python Setup (Recommended)

Use a virtual environment:

python -m venv venv
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

🚀 Running the MCP Server

This project is not run like a normal web server.

Start it using the MCP CLI:

mcp dev server.py


This will:

Launch the MCP server

Start the MCP Inspector

Open Inspector in your browser automatically

🧪 Testing with MCP Inspector
1️⃣ Load a Postman Collection

Use the tool:

load_postman_collection_tool

Input:

Paste the entire Postman collection JSON as a string

Expected output:

{
  "status": "ok",
  "indexed_endpoints": 5
}

2️⃣ Ask Questions About the API

Use the tool:

ask_llm

Example input:

{
  "question": "What HTTP method is used to create a user?"
}


Example output:

{
  "question": "What HTTP method is used to create a user?",
  "answer": "The API uses the POST method to create a user."
}


All answers are generated only by the LLM, grounded in the indexed API documentation.

📦 Dependencies

Key libraries used:

mcp-use – MCP server framework

sentence-transformers – Embeddings

faiss-cpu – Vector similarity search

google-generativeai – Google Gemini LLM

python-dotenv – Environment variable loading

numpy – Numerical operations

🧠 Design Philosophy

This project follows MCP-native principles:

Tools over endpoints

Context over raw retrieval

LLM-only answers (no extractive APIs)

Clean separation of concerns

Minimal, inspectable, and debuggable design

📜 License

MIT License

🙌 Acknowledgements

Model Context Protocol (MCP)

Google Generative AI

SentenceTransformers

FAISS