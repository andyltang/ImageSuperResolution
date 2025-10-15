import { useState, useRef } from "react";

const server_url = "http://localhost:8000/";

export default function ImageUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [upscaledImage, setUpscaledImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [draggingOver, setDragOver] = useState(false);

  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setUpscaledImage(null);
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setUpscaledImage(null);
    setDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    if (e.currentTarget.contains(e.relatedTarget)) {
      // ignore if dragging over child components
      return;
    }
    setDragOver(false);
  }

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      const response = await fetch(server_url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      // Convert response to blob
      const json = await response.json();
      console.log(JSON.stringify(json));
      setUpscaledImage(json['upscaled']);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1>AI Image Upscaler</h1>
      <div
        style={{
          border: "2px dashed #ccc",
          padding: "2em 4em",
          textAlign: "center",
          borderRadius: "8px",
          opacity: draggingOver ? 0.8 : 1
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <h2>Upload an Image</h2>

        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          accept="image/*"
          onChange={handleFileChange}
        />

        <button onClick={handleButtonClick} style={{ marginBottom: "10px" }}>
          Browse File
        </button>

        {preview && (
          <div style={{ margin: "10px 0" }}>
            <h4>Selected Image</h4>
            <img
              src={preview}
              alt="Preview"
              style={{ borderRadius: "4px" }}
            />
          </div>
        )}

        <br />
        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          style={{ margin: "10px 0" }}
        >
          {loading ? "Upscaling..." : "Upscale!"}
        </button>

        {upscaledImage && (
          <div style={{ marginTop: "20px" }}>
            <h4>Upscaled Image</h4>
            <a href={upscaledImage}>Link to image</a>
          </div>
        )}
      </div>
    </>
  );
}
