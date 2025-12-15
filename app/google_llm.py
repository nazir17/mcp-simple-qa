import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set in environment")

genai.configure(api_key=GOOGLE_API_KEY)

# Lightweight wrapper
def generate_answer(question: str, context: str) -> str:
    """
    Uses Google Gemini to generate an answer
    strictly based on provided context.
    """

    prompt = f"""
You are a document-based assistant.

Rules:
- Answer ONLY using the context below.
- If the answer is not in the context, say:
  "I cannot find this information in the document."
- Be concise and factual.

CONTEXT:
{context}

QUESTION:
{question}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text.strip()
