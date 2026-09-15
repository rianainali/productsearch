import { useState, useEffect } from "react";
import ChatInterface from "./components/ChatInterface";
import ProductForm from "./components/ProductForm";
import { getProducts } from "./services/api";
import type { ProductData } from "./types";

type Tab = "search" | "admin";

export default function App() {
  const [tab, setTab] = useState<Tab>("search");
  const [products, setProducts] = useState<ProductData[]>([]);
  const [editingProduct, setEditingProduct] = useState<ProductData | null>(null);

  const fetchProducts = () => {
    getProducts().then(setProducts).catch(console.error);
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <h1 className="text-xl font-bold text-gray-900">ProductSearch</h1>
        <nav className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setTab("search")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === "search"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Search
          </button>
          <button
            onClick={() => setTab("admin")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === "admin"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Admin
          </button>
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-hidden">
        {tab === "search" ? (
          <ChatInterface />
        ) : (
          <div className="h-full overflow-y-auto">
            <div className="max-w-5xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Form */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    {editingProduct ? "Edit Product" : "Add Product"}
                  </h2>
                  <ProductForm
                    onProductAdded={fetchProducts}
                    editingProduct={editingProduct}
                    onCancelEdit={() => setEditingProduct(null)}
                  />
                </div>
              </div>

              {/* Catalog */}
              <div className="lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Catalog
                  </h2>
                  <span className="text-sm text-gray-500">
                    {products.length} products
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {products.map((p) => (
                    <div
                      key={p.id}
                      className={`bg-white rounded-lg shadow-sm border p-4 ${
                        editingProduct?.id === p.id
                          ? "border-blue-500 ring-2 ring-blue-200"
                          : "border-gray-200"
                      }`}
                    >
                      <div className="flex gap-3">
                        {p.image_base64 ? (
                          <img
                            src={`data:image/jpeg;base64,${p.image_base64}`}
                            alt={p.title}
                            className="w-16 h-16 object-cover rounded"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center text-gray-400 text-xl shrink-0">
                            ?
                          </div>
                        )}
                        <div className="min-w-0 flex-1">
                          <h3 className="font-medium text-gray-900 text-sm truncate">
                            {p.title}
                          </h3>
                          <p className="text-gray-500 text-xs line-clamp-2 mt-0.5">
                            {p.description}
                          </p>
                          <p className="text-blue-600 font-bold text-sm mt-1">
                            {p.price.toFixed(2)} $
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setEditingProduct(p)}
                          className="text-gray-400 hover:text-blue-600 transition-colors shrink-0"
                          title="Edit product"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                            />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
