# ProductSearch — Multimodal Semantic Product Search

Search products using natural language, images, or both. Powered by Gemini embeddings and Groq LLaMA.

## Stack

- **Backend**: Python 3.12, FastAPI, NumPy (in-memory vector store)
- **Embeddings**: Google Gemini Embedding API (`gemini-embedding-001`, 3072-dim)
- **Chat**: Groq LLaMA 3.3 70B (streamed responses)
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite

## Prerequisites

- Python 3.12+
- Node.js 18+
- Google API key (Gemini)
- Groq API key

## Setup

### 1. Clone and configure

```bash
cp .env.example backend/.env
```

Edit `backend/.env` with your API keys:

```
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key
```

### 2. Backend

```bash
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --port 8000
```

The server loads 16 seed products on startup (~10s), then serves:

| Method | Route | Description |
|--------|-------|-------------|
| GET | /health | Status + product count |
| GET | /products | List all products |
| POST | /products | Add a product (multipart form) |
| POST | /search | Semantic search (JSON) |
| POST | /chat | Chat with streaming (SSE) |

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dev server proxies API calls to the backend.

## Usage

- **Search tab**: Type a query ("wireless headphones") or upload an image to find similar products. The assistant responds conversationally with matching product cards.
- **Admin tab**: Add new products with title, description, characteristics, price, and an optional image. Products are immediately searchable.

## Tests

```bash
cd backend
python -m pytest tests/ -v
```
