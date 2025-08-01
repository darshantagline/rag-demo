import os
import uuid
import glob
import pdfplumber
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient, models
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "rag_demo"

client = QdrantClient(QDRANT_URL)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def parse_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
    return text

def parse_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=100):
    """
    Split text into sentence-based chunks of up to chunk_size words,
    ensuring sentences are not cut mid-way.
    """
    # Split into sentences
    sentences = re.split(r'(?<=[\.!?])\s+', text.strip())
    chunks = []
    current = ""
    for sentence in sentences:
        # If adding this sentence stays within chunk_size
        if len((current + " " + sentence).split()) <= chunk_size:
            current = (current + " " + sentence).strip()
        else:
            # finalize the current chunk
            if current:
                chunks.append(current)
            # If the sentence itself larger than chunk_size, split by words
            words = sentence.split()
            if len(words) > chunk_size:
                for i in range(0, len(words), chunk_size):
                    chunks.append(" ".join(words[i:i+chunk_size]))
                current = ""
            else:
                current = sentence
    # Append any remaining text
    if current:
        chunks.append(current)
    return chunks


def embed_chunks(chunks):
    embeddings = []
    for chunk in chunks:
        resp = openai_client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embeddings.append(resp.data[0].embedding)
    return embeddings

def ingest_to_qdrant(chunks, embeddings, metadata):
    # Create collection if it doesn't exist
    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            COLLECTION_NAME,
            vectors_config=models.VectorParams(size=len(embeddings[0]), distance="Cosine")
        )
    points = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        # Use a UUID for each chunk as point ID
        unique_id = str(uuid.uuid4())
        points.append(models.PointStruct(
            id=unique_id,
            vector=emb,
            payload={"text": chunk, **metadata[idx]}
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def main():
    files = glob.glob("../sample_docs/*")
    all_chunks, all_embeddings, all_metadata = [], [], []
    for f in files:
        ext = f.split(".")[-1].lower()
        if ext == "html":
            text = parse_html(f)
        elif ext == "pdf":
            text = parse_pdf(f)
        else:
            continue
        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)
        metadata = [{"source": os.path.basename(f), "chunk_idx": i} for i in range(len(chunks))]
        all_chunks.extend(chunks)
        all_embeddings.extend(embeddings)
        all_metadata.extend(metadata)
    if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
        client.delete_collection(COLLECTION_NAME)
    if all_chunks:
        ingest_to_qdrant(all_chunks, all_embeddings, all_metadata)
        print(f"Ingested {len(all_chunks)} chunks into Qdrant.")
    else:
        print("No supported files found for ingestion.")

if __name__ == "__main__":
    main()
