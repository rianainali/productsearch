import base64
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.genai.errors import APIError as GeminiAPIError
from groq import APIError as GroqAPIError

from chat_service import ChatService
from config import Settings
from embedding_service import EmbeddingService, UnsupportedImageError
from models import ProductData, SearchRequest, SearchResult
from seed_data import load_seed_products
from vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

settings = Settings()
embed_svc = EmbeddingService(settings)
vector_store = InMemoryVectorStore()
chat_svc = ChatService(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_seed_products(vector_store, embed_svc)
    yield


app = FastAPI(title="ProductSearch API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- GET /health ---
@app.get("/health")
async def health():
    return {"status": "ok", "product_count": vector_store.count}


# --- GET /products ---
@app.get("/products", response_model=list[ProductData])
async def list_products():
    return list(reversed(vector_store.products))


# --- POST /products ---
@app.post("/products", status_code=201)
async def add_product(
    title: str = Form(...),
    description: str = Form(...),
    characteristics: str = Form(""),
    price: float = Form(...),
    image: UploadFile | None = File(None),
):
    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()

    chars = [c.strip() for c in characteristics.split(",") if c.strip()]

    product = ProductData(
        title=title,
        description=description,
        characteristics=chars,
        price=price,
        image_base64=image_base64,
    )

    try:
        embedding = embed_svc.embed_product(product)
    except UnsupportedImageError as e:
        logger.warning("Unsupported image format: %s", e)
        raise HTTPException(415, str(e)) from e
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    vector_store.add(product, embedding)
    return {"product_id": product.id}


# --- PUT /products/{id} ---
@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    title: str = Form(...),
    description: str = Form(...),
    characteristics: str = Form(""),
    price: float = Form(...),
    image: UploadFile | None = File(None),
    keep_image: str = Form("false"),
):
    existing = next((p for p in vector_store.products if p.id == product_id), None)
    if not existing:
        raise HTTPException(404, "Product not found")

    image_base64 = ""
    if image:
        content = await image.read()
        image_base64 = base64.b64encode(content).decode()
    elif keep_image == "true":
        image_base64 = existing.image_base64

    chars = [c.strip() for c in characteristics.split(",") if c.strip()]

    product = ProductData(
        id=product_id,
        title=title,
        description=description,
        characteristics=chars,
        price=price,
        image_base64=image_base64,
        created_at=existing.created_at,
    )

    try:
        embedding = embed_svc.embed_product(product)
    except UnsupportedImageError as e:
        logger.warning("Unsupported image format: %s", e)
        raise HTTPException(415, str(e)) from e
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    vector_store.update(product_id, product, embedding)
    return {"product_id": product_id}


# --- POST /search ---
@app.post("/search", response_model=list[SearchResult])
async def search(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            logger.warning("Unsupported image format: %s", e)
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.exception("Image description failed")
            raise HTTPException(
                502,
                f"Service d'analyse d'image indisponible: {type(e).__name__}: {e}",
            ) from e

    try:
        query_embedding = embed_svc.embed_query(
            text=request.text, image_description=image_description
        )
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Service d'embedding indisponible") from e

    return vector_store.search(query_embedding, top_k=settings.TOP_K_RESULTS)


# --- POST /chat ---
@app.post("/chat")
async def chat(request: SearchRequest):
    if not request.text and not request.image_base64:
        raise HTTPException(422, "At least one of text or image_base64 is required")

    image_description = None
    if request.image_base64:
        image_bytes = base64.b64decode(request.image_base64)
        try:
            image_description = embed_svc.describe_image(image_bytes)
        except UnsupportedImageError as e:
            logger.warning("Unsupported image format: %s", e)
            raise HTTPException(415, str(e)) from e
        except Exception as e:
            logger.exception("Image description failed")
            raise HTTPException(
                502,
                f"Service d'analyse d'image indisponible: {type(e).__name__}: {e}",
            ) from e

    try:
        query_embedding = embed_svc.embed_query(
            text=request.text, image_description=image_description
        )
    except GeminiAPIError as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(502, "Embedding service unavailable") from e

    results = vector_store.search(query_embedding, top_k=settings.TOP_K_RESULTS)
    user_message = " ".join(filter(None, [request.text, image_description])) or "image search"

    async def event_stream():
        try:
            async for token in chat_svc.generate_response_stream(
                user_message, results
            ):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except GroqAPIError as e:
            logger.error("Chat generation failed: %s", e)
            yield f"data: [ERROR] Chat service unavailable\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
