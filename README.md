# RAG Demo Project

This repo demonstrates a simple Retrieval-Augmented Generation pipeline:

- Parse HTML and PDF documents
- Chunk and add metadata
- Generate embeddings (OpenAI)
- Ingest into Qdrant
- Query via Next.js API route

## Structure
- `rag_demo/python`: Data pipeline (parsing, chunking, embedding, ingestion)
- `rag_demo/nextjs`: Next.js API route
- `rag_demo/sample_docs`: Place sample HTML and PDF files here

## Setup

### 1. Python (Data Pipeline)
- Install dependencies:
  ```bash
  cd rag_demo/python
  pip install -r requirements.txt
  ```
- Add your OpenAI API key to `.env`:
  ```env
  OPENAI_API_KEY=your-key-here
  QDRANT_URL=http://localhost:6333
  ```
- Run ingestion:
  ```bash
  python ingest.py
  ```

### 2. Qdrant
- [Install Qdrant](https://qdrant.tech/documentation/quick-start/)
- Start Qdrant locally:
  ```bash
  docker run -p 6333:6333 qdrant/qdrant
  ```

### 3. Next.js API
- Install dependencies:
  ```bash
  cd rag_demo/nextjs
  npm install
  ```
- Start dev server:
  ```bash
  npm run dev
  ```
- Query API route `http://localhost:3000/api/rag?question=...`

### 4. FastAPI Server
- Activate the Python virtual environment:
  ```bash
  cd rag_demo/python
  source env/bin/activate
  ```
- Install Python requirements:
  ```bash
  pip install -r requirements.txt
  ```
- Run ingestion:
  ```bash
  python ingest.py
  ```
- Start the FastAPI server:
  ```bash
  uvicorn python.app:app --reload --host 0.0.0.0 --port 8000
  ```
- View the interactive Swagger UI (OpenAPI docs) at: 
  ``` bash
  http://localhost:8000/docs
  ```

- **Note:** Confirm the `RAG_API_URL` in the Next.js client points to the FastAPI server.




## Sample Docs
Place your sample HTML and PDF files in `rag_demo/sample_docs`.

---

## Contact
For questions, open an issue or contact the repo owner.
