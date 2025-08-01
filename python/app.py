import os
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "rag_demo"

client = QdrantClient(QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

class Chunk(BaseModel):
    text: str
    source: str
    chunk_idx: int

@app.get("/api/rag")
def rag_search(question: str = Query(...)):
    # Embed the question
    resp = openai_client.embeddings.create(
        input=question,
        model="text-embedding-3-small"
    )
    query_emb = resp.data[0].embedding
    # Search Qdrant
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_emb,
        limit=5
    )
    retrieved = []
    for point in search_result:
        payload = point.payload
        retrieved.append({
            "text": payload["text"],
            "source": payload["source"],
            "chunk_idx": payload["chunk_idx"]
        })
    return JSONResponse(content={"retrieved_chunks": retrieved})
