from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class ProductData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    characteristics: list[str] = []
    price: float = Field(ge=0)
    image_base64: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SearchResult(BaseModel):
    product: ProductData
    similarity_score: float = Field(ge=0.0, le=1.0)


class SearchRequest(BaseModel):
    text: str | None = None
    image_base64: str | None = None
