import { useCallback, useState, type DragEvent, type ChangeEvent } from "react";

interface Props {
  onImageSelect: (base64: string, file: File) => void;
  preview?: string;
  onClear?: () => void;
}

const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export default function ImageUploader({ onImageSelect, preview, onClear }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");

  const processFile = useCallback(
    (file: File) => {
      setError("");
      if (!file.type.startsWith("image/")) {
        setError("Only image files are accepted.");
        return;
      }
      if (file.size > MAX_SIZE) {
        setError("Image must be under 5MB.");
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(",")[1];
        onImageSelect(base64, file);
      };
      reader.readAsDataURL(file);
    },
    [onImageSelect]
  );

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  return (
    <div className="space-y-2">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        {preview ? (
          <div className="relative inline-block">
            <img
              src={`data:image/jpeg;base64,${preview}`}
              alt="Preview"
              className="max-h-32 rounded mx-auto"
            />
            {onClear && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 text-sm flex items-center justify-center hover:bg-red-600"
              >
                x
              </button>
            )}
          </div>
        ) : (
          <div className="text-gray-500">
            <p className="font-medium">Drop an image here</p>
            <p className="text-sm mt-1">or click to browse</p>
          </div>
        )}
        <input
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
}
