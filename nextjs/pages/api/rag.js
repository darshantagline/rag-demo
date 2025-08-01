// Next.js API route to proxy RAG search to FastAPI backend
import fetch from 'node-fetch';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  const { question } = req.query;
  if (!question) {
    return res.status(400).json({ error: 'Missing question parameter' });
  }
  try {
    // Call FastAPI backend
    const apiUrl = process.env.RAG_API_URL || 'http://localhost:8000/api/rag';
    const response = await fetch(`${apiUrl}?question=${encodeURIComponent(question)}`);
    if (!response.ok) {
      throw new Error('Backend error');
    }
    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
