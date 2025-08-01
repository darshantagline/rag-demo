// nextjs/pages/index.js
export default function Home() {
  return (
    <main style={{ padding: 20 }}>
      <h1>Welcome to your RAG Demo</h1>
      <p>Try querying <code>/rag?question=Hello</code></p>
    </main>
  );
}