import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from chat_service import ChatService, SYSTEM_PROMPT
from models import ProductData, SearchResult


@pytest.fixture
def chat_svc():
    return ChatService()


@pytest.fixture
def sample_results():
    product = ProductData(
        title="Wireless Headphones",
        description="Bluetooth over-ear headphones",
        characteristics=["bluetooth", "ANC"],
        price=79.99,
    )
    return [SearchResult(product=product, similarity_score=0.85)]


def test_format_results(chat_svc, sample_results):
    """_format_results returns valid JSON string with expected fields."""
    import json
    result = chat_svc._format_results(sample_results)
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "Wireless Headphones"
    assert parsed[0]["price"] == 79.99
    assert parsed[0]["similarity_score"] == 0.85


@pytest.mark.anyio
async def test_generate_response(chat_svc, sample_results):
    """generate_response returns a non-empty string from Groq."""
    response = await chat_svc.generate_response(
        "I need headphones", sample_results
    )
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.anyio
async def test_generate_response_stream(chat_svc, sample_results):
    """generate_response_stream yields string tokens."""
    tokens = []
    async for token in chat_svc.generate_response_stream(
        "I need headphones", sample_results
    ):
        tokens.append(token)
        if len(tokens) >= 3:
            break
    assert len(tokens) >= 1
    assert all(isinstance(t, str) for t in tokens)


def test_system_prompt_exists():
    """SYSTEM_PROMPT is a non-empty string."""
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 20
