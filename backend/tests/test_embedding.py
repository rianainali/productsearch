import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from models import ProductData
from embedding_service import EmbeddingService


@pytest.fixture
def embed_svc():
    return EmbeddingService()


@pytest.fixture
def sample_product():
    return ProductData(
        title="Bluetooth Headphones",
        description="Wireless over-ear headphones with noise cancellation",
        characteristics=["bluetooth 5.0", "ANC", "40h battery"],
        price=79.99,
    )


def test_embed_product_happy_path(embed_svc, sample_product):
    """Full product embedding returns a normalized 1408-dim vector."""
    vec = embed_svc.embed_product(sample_product)
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_text_only(embed_svc):
    """Text-only query returns a valid embedding."""
    vec = embed_svc.embed_query(text="red running shoes")
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_image_description_only(embed_svc):
    """Query with only an image description returns a valid embedding."""
    vec = embed_svc.embed_query(image_description="white running shoes with mesh upper")
    assert vec.shape == (3072,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-4


def test_embed_query_no_input(embed_svc):
    """Calling with neither text nor image_description raises ValueError."""
    with pytest.raises(ValueError, match="At least one"):
        embed_svc.embed_query()
