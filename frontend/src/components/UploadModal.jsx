import { useState, useRef } from "react";
import api from "../api/client";

export default function UploadModal({ onClose, onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  const upload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    const form = new FormData();
    files.forEach((f) => form.append("files", f));

    try {
      await api.post("/validate", form);
      if (onUploadComplete) {
        onUploadComplete();
      }
      onClose();
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(err.response?.data?.message || "Failed to upload files");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-[#161616] p-6 rounded-xl w-[400px] border border-gray-800">
        <h2 className="mb-4 text-lg">Upload files</h2>

        <div
          className={`border-2 border-dashed p-8 text-center rounded-lg cursor-pointer transition
            ${isDragging ? "border-blue-500 bg-gray-800" : "border-gray-700"}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          {isDragging ? "Отпустите чтобы загрузить файлы" : "Перетащите .docx файлы или нажмите чтобы выбрать"}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".docx"
          className="hidden"
          onChange={handleFileSelect}
        />

        {files.length > 0 && (
          <ul className="mt-4 max-h-40 overflow-y-auto text-sm text-gray-200">
            {files.map((file, index) => (
              <li
                key={index}
                className="flex justify-between items-center border-b border-gray-700 py-1"
              >
                <span>{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-400"
                >
                  &times;
                </button>
              </li>
            ))}
          </ul>
        )}

        {uploadError && (
          <div className="mt-2 text-red-400 text-sm">
            {uploadError}
          </div>
        )}

        <button
          onClick={upload}
          disabled={isUploading || files.length === 0}
          className={`mt-4 w-full p-2 rounded-lg transition ${
            isUploading || files.length === 0
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-500"
          }`}
        >
          {isUploading ? "Загружается..." : "Начать валидацию"}
        </button>
      </div>
    </div>
  );
}