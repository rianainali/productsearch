import type { SearchResult } from "../types";

interface Props {
  result: SearchResult;
}

function scoreColor(score: number): string {
  if (score >= 0.8) return "bg-green-100 text-green-800";
  if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

export default function ProductCard({ result }: Props) {
  const { product, similarity_score } = result;
  const pct = Math.round(similarity_score * 100);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col">
      {product.image_base64 ? (
        <img
          src={`data:image/jpeg;base64,${product.image_base64}`}
          alt={product.title}
          className="w-full h-40 object-cover"
        />
      ) : (
        <div className="w-full h-40 bg-gray-100 flex items-center justify-center text-gray-400 text-4xl">
          ?
        </div>
      )}
      <div className="p-4 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">
            {product.title}
          </h3>
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-full shrink-0 ${scoreColor(
              similarity_score
            )}`}
          >
            {pct}%
          </span>
        </div>
        <p className="text-gray-600 text-xs mb-3 line-clamp-2 flex-1">
          {product.description}
        </p>
        {product.characteristics.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {product.characteristics.slice(0, 3).map((c) => (
              <span
                key={c}
                className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
              >
                {c}
              </span>
            ))}
          </div>
        )}
        <p className="text-blue-600 font-bold text-lg mt-auto">
          {product.price.toFixed(2)} $
        </p>
      </div>
    </div>
  );
}
