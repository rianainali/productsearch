import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from models import ProductData
from vector_store import InMemoryVectorStore


@pytest.fixture
def store():
    return InMemoryVectorStore()


def _random_embedding(dim=1408):
    vec = np.random.randn(dim).astype(np.float32)
    return vec / np.linalg.norm(vec)


def _make_product(title: str) -> ProductData:
    return ProductData(
        title=title,
        description=f"Description for {title}",
        price=10.0,
    )


def test_add_and_search(store):
    """Adding a product then searching with its own embedding returns score > 0.99."""
    product = _make_product("Test Product")
    embedding = _random_embedding()
    store.add(product, embedding)

    results = store.search(embedding, top_k=5)
    assert len(results) == 1
    assert results[0].product.title == "Test Product"
    assert results[0].similarity_score > 0.99


def test_search_empty_store(store):
    """Searching an empty store returns an empty list."""
    query = _random_embedding()
    results = store.search(query, top_k=5)
    assert results == []


def test_top_k_greater_than_n(store):
    """When top_k > number of products, all products are returned."""
    for i in range(3):
        store.add(_make_product(f"Product {i}"), _random_embedding())

    query = _random_embedding()
    results = store.search(query, top_k=10)
    assert len(results) == 3
