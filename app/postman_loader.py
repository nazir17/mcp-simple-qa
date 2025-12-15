import json
from typing import List, Dict

def load_postman_collection(json_bytes: bytes) -> List[Dict]:
    """
    Converts Postman collection JSON into structured API chunks.
    Each chunk represents one API endpoint.
    """
    collection = json.loads(json_bytes)
    chunks = []

    def walk_items(items, folder_name=""):
        for item in items:
            if "item" in item:
                walk_items(item["item"], item.get("name", folder_name))
            else:
                request = item.get("request", {})
                if not request:
                    continue

                method = request.get("method", "")
                url = request.get("url", {})
                endpoint = ""

                if isinstance(url, dict):
                    path = []
                    if isinstance(url, dict):
                        path = url.get("path", [])
                    elif isinstance(url, str):
                        continue

                    if not path:
                        continue

                    endpoint = "/" + "/".join(path)
                elif isinstance(url, str):
                    endpoint = url

                headers = request.get("header", [])
                header_text = "\n".join(
                    f"{h.get('key')}: {h.get('value')}" for h in headers
                )

                body = request.get("body", {})
                body_text = ""
                if body.get("mode") == "raw":
                    body_text = body.get("raw", "")

                description = request.get("description", "")

                chunk_text = f"""
API NAME: {item.get("name")}

FOLDER: {folder_name}

METHOD: {method}
ENDPOINT: {endpoint}

DESCRIPTION:
{description}

HEADERS:
{header_text or "None"}

REQUEST BODY:
{body_text or "None"}
""".strip()

                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "method": method,
                        "endpoint": endpoint,
                        "folder": folder_name,
                        "source": "postman"
                    }
                })

    walk_items(collection.get("item", []))
    return chunks