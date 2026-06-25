import { useEffect, useRef, useState } from "react";
import Icon from "./Icon.jsx";

export default function Dropzone({ file, onFile, accept, hint }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (file && file.type && file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
    setPreviewUrl(null);
  }, [file]);

  const handleFiles = (files) => {
    if (files && files[0]) onFile(files[0]);
  };

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      style={{
        border: `1.5px dashed ${dragging ? "var(--accent)" : "var(--border-strong)"}`,
        borderRadius: "var(--radius)",
        padding: previewUrl ? 14 : "30px 20px",
        textAlign: "center",
        cursor: "pointer",
        background: dragging ? "var(--surface-alt)" : "var(--surface)",
        transition: "all .12s ease",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => handleFiles(e.target.files)}
      />

      {previewUrl ? (
        <div style={{ display: "flex", alignItems: "center", gap: 14, textAlign: "left" }}>
          <img
            src={previewUrl}
            alt="preview"
            style={{
              width: 64,
              height: 64,
              objectFit: "cover",
              borderRadius: 6,
              border: "1px solid var(--border)",
              flexShrink: 0,
            }}
          />
          <div>
            <div style={{ fontWeight: 600, fontSize: 13.5, marginBottom: 3 }}>{file.name}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {(file.size / 1024).toFixed(0)} KB · click or drop to replace
            </div>
          </div>
        </div>
      ) : (
        <>
          <div
            style={{
              color: "var(--text-faint)",
              marginBottom: 8,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <Icon name="upload" size={22} />
          </div>
          <div style={{ fontWeight: 600, fontSize: 13.5, marginBottom: 3 }}>
            {file ? file.name : "Drop a file here, or click to choose"}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{hint}</div>
        </>
      )}
    </div>
  );
}
