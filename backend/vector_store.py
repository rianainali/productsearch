import numpy as np

from models import ProductData, SearchResult


class InMemoryVectorStore:
    def __init__(self):
        self.vectors: np.ndarray | None = None
        self.products: list[ProductData] = []

    @property
    def count(self) -> int:
        return len(self.products)

    def add(self, product: ProductData, embedding: np.ndarray) -> None:
        embedding = embedding.reshape(1, -1)
        if self.vectors is None:
            self.vectors = embedding
        else:
            self.vectors = np.vstack([self.vectors, embedding])
        self.products.append(product)

    def update(
        self, product_id: str, product: ProductData, embedding: np.ndarray
    ) -> bool:
        for i, p in enumerate(self.products):
            if p.id == product_id:
                self.products[i] = product
                self.vectors[i] = embedding.reshape(-1)
                return True
        return False

    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> list[SearchResult]:
        if self.vectors is None or len(self.products) == 0:
            return []

        scores = self.vectors @ query_embedding
        k = min(top_k, len(self.products))
        top_indices = np.argsort(scores)[::-1][:k]

        return [
            SearchResult(
                product=self.products[i],
                similarity_score=float(np.clip(scores[i], 0.0, 1.0)),
            )
            for i in top_indices
        ]
