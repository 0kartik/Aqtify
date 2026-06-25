import { useState } from "react";
import Button from "./Button.jsx";
import Icon from "./Icon.jsx";
import { inputStyle } from "../styles.js";
import { createApiKey } from "../api/client.js";

export default function KeyBar({ apiBase, apiKey, onChange }) {
  const [status, setStatus] = useState(apiKey ? "key loaded" : "no key set");
  const [creating, setCreating] = useState(false);
  const [revealed, setRevealed] = useState(false);

  const save = (val) => {
    onChange(val);
    localStorage.setItem("aqtify_api_key", val);
    setStatus(val ? "key saved" : "no key set");
  };

  const handleCreate = async () => {
    setCreating(true);
    setStatus("creating…");
    try {
      const data = await createApiKey(apiBase, { keyMode: "server" });
      save(data.api_key);
      setRevealed(true);
      setStatus("new key saved (custodial)");
    } catch {
      setStatus("API offline");
    }
    setCreating(false);
  };

  const copy = async () => {
    if (!apiKey) return;
    try {
      await navigator.clipboard.writeText(apiKey);
      setStatus("copied to clipboard");
      setTimeout(() => setStatus(apiKey ? "key loaded" : "no key set"), 1500);
    } catch {
      setStatus("could not copy");
    }
  };

  return (
    <div
      style={{
        maxWidth: 920,
        margin: "16px auto 0",
        padding: "0 24px",
        display: "flex",
        gap: 10,
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      <div style={{ position: "relative", flex: 1, minWidth: 240 }}>
        <input
          value={apiKey}
          onChange={(e) => save(e.target.value)}
          placeholder="Paste your API key (aqt_...)"
          type={revealed ? "text" : "password"}
          style={{ ...inputStyle, width: "100%", paddingRight: 70 }}
          className="mono"
        />
        <div style={{ position: "absolute", right: 6, top: 5, display: "flex", gap: 2 }}>
          <button
            type="button"
            onClick={() => setRevealed((r) => !r)}
            title={revealed ? "Hide key" : "Show key"}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: 6,
              color: "var(--text-muted)",
              display: "flex",
            }}
          >
            <Icon name={revealed ? "eyeOff" : "eye"} size={15} />
          </button>
          <button
            type="button"
            onClick={copy}
            title="Copy key"
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: 6,
              color: "var(--text-muted)",
              display: "flex",
            }}
          >
            <Icon name="copy" size={15} />
          </button>
        </div>
      </div>
      <Button variant="secondary" onClick={handleCreate} disabled={creating}>
        <Icon name="key" size={14} /> Create key
      </Button>
      <span style={{ fontSize: 11.5, color: "var(--text-faint)" }}>{status}</span>
    </div>
  );
}
