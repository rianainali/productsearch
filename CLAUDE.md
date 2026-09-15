# ProductSearch — Multimodal Semantic Product Search

## Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend | Python 3.12 / FastAPI + Uvicorn | API REST + service orchestration |
| Embedding | Gemini Embedding API (`gemini-embedding-001`) | 3072-dim vectors (PRD said 1408 with gemini-2.0-flash — corrected after testing) |
| Vector store | In-memory NumPy | Cosine similarity, matrix shape (N, 3072) |
| LLM chatbot | Groq — LLaMA 3.3 70B (`llama-3.3-70b-versatile`) | Streamed conversational responses |
| Frontend | React 18 + TypeScript + TailwindCSS + Vite | Chat UI + product form |

## Project structure

```
ProductSearch/
├── backend/
│   ├── config.py                # Settings (pydantic-settings, reads .env)
│   ├── models.py                # ProductData, SearchResult, SearchRequest
│   ├── embedding_service.py     # EmbeddingService (Gemini)
│   ├── vector_store.py          # InMemoryVectorStore (NumPy)
│   ├── chat_service.py          # ChatService (Groq)
│   ├── seed_data.py             # SEED_PRODUCTS (16 items) + load_seed_products()
│   ├── main.py                  # FastAPI app + lifespan + all routes
│   └── tests/
│       ├── test_embedding.py    # 4 tests (happy path, text-only, image-only, no input)
│       ├── test_vector_store.py # 3 tests (add/search, empty store, top_k > N)
│       ├── test_api.py          # 5 tests (health, list, search, empty query, add)
│       └── test_chat_service.py # 4 tests (format, response, stream, prompt)
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatInterface.tsx # Chat UI with streaming + product cards
│       │   ├── ProductForm.tsx   # Add product form with validation
│       │   ├── ProductCard.tsx   # Product card with score color coding
│       │   └── ImageUploader.tsx # Drag & drop image with preview
│       ├── services/
│       │   ├── api.ts           # HTTP calls (getProducts, addProduct, searchProducts)
│       │   └── chatStream.ts    # SSE streaming client
│       ├── types/
│       │   └── index.ts         # TS types mirroring Pydantic models
│       └── App.tsx              # Main layout with Search/Admin tabs
├── frontend/e2e/
│   └── product-search.spec.ts   # 4 Playwright E2E tests
├── .env.example                 # Environment variable template
├── requirements.txt             # Python dependencies
├── CODING_PLAN.md               # Full implementation plan
└── multimodal_search_prd_techspec.md  # Original PRD + Tech Spec
```

## Completed phases

### Phase 0 — Foundation
- `backend/config.py` — `Settings` class with `GOOGLE_API_KEY`, `GROQ_API_KEY`, `TOP_K_RESULTS`, `EMBEDDING_MODEL`, `GROQ_MODEL`
- `backend/models.py` — Pydantic models: `ProductData` (UUID4 id, title, description, characteristics, price, image_base64, created_at), `SearchResult`, `SearchRequest`
- `.env.example`, `requirements.txt`

### Phase 1 — AI Services & Storage
- `backend/embedding_service.py` — `EmbeddingService` using `google-genai` SDK. `embed_product()` and `embed_query()` return normalized L2 vectors (3072-dim). Image-only queries use a text placeholder since Gemini embedding requires text content.
- `backend/vector_store.py` — `InMemoryVectorStore` with vectorized cosine similarity via NumPy.
- `backend/chat_service.py` — `ChatService` with `generate_response()` (non-stream) and `generate_response_stream()` (SSE) via Groq SDK.
- 7/7 tests pass. Integration test: embed + store + search returns score > 0.99.

### Phase 2 — Seed Data
- `backend/seed_data.py` — 16 products across 5 categories (electronics, clothing, home, sports, office). `load_seed_products()` with exponential backoff on 429 errors. Loads in ~10s.
- Search "casque bluetooth" returns "Wireless Bluetooth Headphones" as top-1 (score 0.650).

### Phase 3 — FastAPI API
- `backend/main.py` — FastAPI app with lifespan (seeds 16 products on startup), CORS middleware, endpoints:
  - `GET /health` -> `{"status": "ok", "product_count": N}`
  - `GET /products` -> all products (reverse chronological)
  - `POST /products` (multipart/form-data) -> 201 + `{"product_id": "..."}`
  - `POST /search` (JSON `{text?, image_base64?}`) -> `list[SearchResult]` top-K
  - `POST /chat` (JSON `{text?, image_base64?}`) -> SSE stream (token-by-token)
  - Empty search/chat requests return 422
- `backend/tests/test_api.py` — 5 tests, all passing
- Server starts in ~10s, all endpoints verified via curl

### Phase 4 — React Frontend
- Vite + React 18 + TypeScript + TailwindCSS v4 (via `@tailwindcss/vite` plugin)
- Vite dev server proxies `/api/*` to backend on port 8000
- Two tabs: **Search** (chat interface) and **Admin** (product form + catalog)
- `ChatInterface.tsx` — text + image input, SSE streaming response, product cards grid
- `ProductForm.tsx` — validated form with `ImageUploader` drag & drop
- `ProductCard.tsx` — image, title, price, similarity score with color coding (green/yellow/red)
- `api.ts` / `chatStream.ts` — HTTP + SSE services
- Zero TypeScript errors, production build passes (203KB JS gzipped to 63KB)

### Phase 5 — Tests & Polish
- 16/16 backend tests pass (pytest): embedding (4), vector store (3), API (5), chat service (4)
- Backend line coverage: 86% (target 80%)
- 4/4 Playwright E2E tests pass: homepage load, admin catalog, add product, search with results
- Error handling: Gemini API errors return 502, Groq stream errors yield `[ERROR]` SSE event
- `README.md` with setup instructions, API docs, usage guide

## Code conventions

- Language: all code, comments, variable names, and docstrings in **English**
- Backend: Python 3.12, type hints everywhere, Pydantic models for data validation
- Formatting: double quotes for strings, 4-space indentation
- Imports: stdlib first, then third-party, then local (separated by blank lines)
- Tests: pytest, files prefixed with `test_`, fixtures for shared setup
- SDK: using `google-genai` package (not `google-generativeai`) — import as `from google import genai`
- Frontend: React functional components, hooks, TypeScript strict mode
- Styling: TailwindCSS utility classes only (no custom CSS)
- API proxy: frontend dev server proxies `/api/*` -> `http://localhost:8000/`

## How to run

```bash
# Backend (port 8000)
cd backend && python -m uvicorn main:app --port 8000

# Frontend (port 5173)
cd frontend && npm run dev
```

## Key corrections from PRD

| PRD assumption | Actual | Reason |
|---------------|--------|--------|
| `gemini-2.0-flash` for embeddings | `gemini-embedding-001` | gemini-2.0-flash does not support `embedContent` |
| 1408-dim vectors | 3072-dim vectors | gemini-embedding-001 outputs 3072 dimensions |
| `google-generativeai` SDK | `google-genai` SDK | newer official SDK with cleaner API |
