import { useState } from "react";
import Panel from "../components/Panel.jsx";
import Field from "../components/Field.jsx";
import { inputStyle } from "../styles.js";
import Button from "../components/Button.jsx";
import Icon from "../components/Icon.jsx";
import ErrorBox from "../components/ErrorBox.jsx";
import { registerBulk } from "../api/client.js";

export default function BulkRegisterPanel({ apiBase, apiKey }) {
  const [files, setFiles] = useState([]);
  const [ownerName, setOwnerName] = useState("");
  const [ownerEmail, setOwnerEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFiles = (fileList) => setFiles(Array.from(fileList).slice(0, 50));

  const run = async () => {
    setError("");
    setResult(null);
    if (files.length === 0) return setError("Choose one or more files first.");
    if (!apiKey) return setError("Set an API key above first.");

    setBusy(true);
    try {
      const data = await registerBulk(apiBase, apiKey, { files, ownerName, ownerEmail });
      setResult(data);
    } catch (e) {
      setError(e.message || `Could not reach the API at ${apiBase}. Is the backend running?`);
    }
    setBusy(false);
  };

  return (
    <Panel
      title="Bulk registration"
      subtitle="Register up to 50 files in one call. Each file gets its own AI gate check and certificate — one bad file doesn't abort the batch."
    >
      <div
        onClick={() => document.getElementById("bulk-file-input").click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFiles(e.dataTransfer.files);
        }}
        style={{
          border: "1.5px dashed var(--border-strong)",
          borderRadius: "var(--radius)",
          padding: "30px 20px",
          textAlign: "center",
          cursor: "pointer",
          background: "var(--surface)",
        }}
      >
        <input
          id="bulk-file-input"
          type="file"
          multiple
          accept="image/*,audio/*,video/*"
          style={{ display: "none" }}
          onChange={(e) => handleFiles(e.target.files)}
        />
        <Icon name="layers" size={22} />
        <div style={{ fontWeight: 600, fontSize: 13.5, margin: "8px 0 3px" }}>
          {files.length > 0 ? `${files.length} file${files.length > 1 ? "s" : ""} selected` : "Drop multiple files, or click to choose"}
        </div>
        <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Up to 50 files per batch</div>
      </div>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 16 }}>
        <div style={{ flex: 1, minWidth: 180 }}>
          <Field label="Owner name (optional, applies to all)">
            <input style={inputStyle} value={ownerName} onChange={(e) => setOwnerName(e.target.value)} placeholder="Jane Doe" />
          </Field>
        </div>
        <div style={{ flex: 1, minWidth: 180 }}>
          <Field label="Owner email (optional, applies to all)">
            <input style={inputStyle} value={ownerEmail} onChange={(e) => setOwnerEmail(e.target.value)} placeholder="jane@example.com" />
          </Field>
        </div>
      </div>

      <Button onClick={run} disabled={busy} style={{ width: "100%", marginTop: 8 }}>
        <Icon name="layers" size={15} /> {busy ? "Registering batch…" : `Register ${files.length || ""} file${files.length === 1 ? "" : "s"}`}
      </Button>
      <ErrorBox message={error} />

      {result && (
        <div style={{ marginTop: 22 }}>
          <div style={{ display: "flex", gap: 16, marginBottom: 14, fontSize: 13 }}>
            <span><b style={{ color: "var(--success)" }}>{result.succeeded}</b> succeeded</span>
            <span><b style={{ color: "var(--danger)" }}>{result.failed}</b> failed</span>
            <span style={{ color: "var(--text-muted)" }}>{result.total} total</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {result.results.map((r, i) => (
              <div
                key={i}
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  padding: "10px 14px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 10,
                  background: r.status === "success" ? "var(--success-bg)" : "var(--danger-bg)",
                }}
              >
                <div style={{ fontSize: 12.5 }}>{r.file_name}</div>
                <div
                  className="mono"
                  style={{
                    fontSize: 11.5,
                    fontWeight: 600,
                    color: r.status === "success" ? "var(--success)" : "var(--danger)",
                  }}
                >
                  {r.status === "success" ? r.certificate_id : r.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}
