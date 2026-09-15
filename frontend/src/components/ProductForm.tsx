import { useState, useEffect, type FormEvent } from "react";
import { addProduct, updateProduct } from "../services/api";
import type { ProductData } from "../types";
import ImageUploader from "./ImageUploader";

interface Props {
  onProductAdded: () => void;
  editingProduct?: ProductData | null;
  onCancelEdit?: () => void;
}

export default function ProductForm({ onProductAdded, editingProduct, onCancelEdit }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [characteristics, setCharacteristics] = useState("");
  const [price, setPrice] = useState("");
  const [imageBase64, setImageBase64] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [keepImage, setKeepImage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (editingProduct) {
      setTitle(editingProduct.title);
      setDescription(editingProduct.description);
      setCharacteristics(editingProduct.characteristics.join(", "));
      setPrice(String(editingProduct.price));
      setImageBase64(editingProduct.image_base64 || "");
      setImageFile(null);
      setKeepImage(!!editingProduct.image_base64);
      setMessage("");
    } else {
      resetForm();
    }
  }, [editingProduct]);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setCharacteristics("");
    setPrice("");
    setImageBase64("");
    setImageFile(null);
    setKeepImage(false);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title || !description || !price) return;

    setLoading(true);
    setMessage("");

    try {
      const form = new FormData();
      form.append("title", title);
      form.append("description", description);
      form.append("characteristics", characteristics);
      form.append("price", price);
      if (imageFile) {
        form.append("image", imageFile);
      }

      if (editingProduct) {
        form.append("keep_image", keepImage && !imageFile ? "true" : "false");
        await updateProduct(editingProduct.id, form);
        setMessage("Product updated successfully!");
        onCancelEdit?.();
      } else {
        await addProduct(form);
        setMessage("Product added successfully!");
        resetForm();
      }
      onProductAdded();
    } catch {
      setMessage(editingProduct ? "Failed to update product." : "Failed to add product.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={100}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="Product name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description *
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          required
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
          placeholder="Describe the product"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Characteristics
        </label>
        <input
          type="text"
          value={characteristics}
          onChange={(e) => setCharacteristics(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="bluetooth, wireless, waterproof (comma-separated)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Price *
        </label>
        <input
          type="number"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          min={0}
          step={0.01}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="0.00"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Image
        </label>
        <ImageUploader
          onImageSelect={(base64, file) => {
            setImageBase64(base64);
            setImageFile(file);
            setKeepImage(false);
          }}
          preview={imageBase64}
          onClear={() => {
            setImageBase64("");
            setImageFile(null);
            setKeepImage(false);
          }}
        />
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading || !title || !description || !price}
          className="flex-1 bg-blue-600 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading
            ? editingProduct
              ? "Updating..."
              : "Adding..."
            : editingProduct
              ? "Update Product"
              : "Add Product"}
        </button>
        {editingProduct && (
          <button
            type="button"
            onClick={() => {
              onCancelEdit?.();
              resetForm();
            }}
            disabled={loading}
            className="px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {message && (
        <p
          className={`text-sm text-center ${
            message.includes("success") ? "text-green-600" : "text-red-600"
          }`}
        >
          {message}
        </p>
      )}
    </form>
  );
}
