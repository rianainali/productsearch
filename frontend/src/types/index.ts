export interface ProductData {
  id: string;
  title: string;
  description: string;
  characteristics: string[];
  price: number;
  image_base64: string;
  created_at: string;
}

export interface SearchResult {
  product: ProductData;
  similarity_score: number;
}

export interface SearchRequest {
  text?: string;
  image_base64?: string;
}
