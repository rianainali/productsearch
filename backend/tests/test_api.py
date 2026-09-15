import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    from main import app, vector_store, embed_svc
    from models import ProductData
    import numpy as np

    # Skip lifespan seed loading — add one product manually for tests
    product = ProductData(
        title="Test Headphones",
        description="Wireless bluetooth headphones",
        characteristics=["bluetooth", "wireless"],
        price=49.99,
    )
    fake_embedding = np.random.randn(3072).astype(np.float32)
    fake_embedding /= np.linalg.norm(fake_embedding)
    vector_store.add(product, fake_embedding)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Cleanup
    vector_store.products.clear()
    vector_store.vectors = None


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["product_count"] >= 1


@pytest.mark.anyio
async def test_list_products(client):
    resp = await client.get("/products")
    assert resp.status_code == 200
    products = resp.json()
    assert len(products) >= 1
    assert products[0]["title"] == "Test Headphones"


@pytest.mark.anyio
async def test_search(client):
    resp = await client.post("/search", json={"text": "headphones"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert "product" in results[0]
    assert "similarity_score" in results[0]


@pytest.mark.anyio
async def test_search_empty_query(client):
    resp = await client.post("/search", json={})
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_add_product(client):
    resp = await client.post(
        "/products",
        data={
            "title": "New Speaker",
            "description": "Portable bluetooth speaker",
            "characteristics": "bluetooth, waterproof",
            "price": "29.99",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "product_id" in data
