import type { ProductData, SearchResult } from "../types";

const BASE = "/api";

export async function getProducts(): Promise<ProductData[]> {
  const res = await fetch(`${BASE}/products`);
  if (!res.ok) throw new Error("Failed to fetch products");
  return res.json();
}

export async function addProduct(form: FormData): Promise<string> {
  const res = await fetch(`${BASE}/products`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Failed to add product");
  const data = await res.json();
  return data.product_id;
}

export async function updateProduct(id: string, form: FormData): Promise<string> {
  const res = await fetch(`${BASE}/products/${id}`, {
    method: "PUT",
    body: form,
  });
  if (!res.ok) throw new Error("Failed to update product");
  const data = await res.json();
  return data.product_id;
}

export async function searchProducts(
  text?: string,
  imageBase64?: string
): Promise<SearchResult[]> {
  const res = await fetch(`${BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, image_base64: imageBase64 }),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}
