import { useState } from "react";
import Icon from "./Icon.jsx";

export default function DataRow({ k, v, copyable }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(String(v));
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* clipboard unavailable — silently ignore */
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: 12,
        padding: "7px 0",
        borderBottom: "1px solid var(--border)",
        fontSize: 12.5,
      }}
    >
      <span style={{ color: "var(--text-muted)" }}>{k}</span>
      <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span className="mono" style={{ color: "var(--text)", wordBreak: "break-all", textAlign: "right" }}>
          {String(v)}
        </span>
        {copyable && (
          <button
            type="button"
            onClick={copy}
            title="Copy"
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: 2,
              color: copied ? "var(--success)" : "var(--text-faint)",
              display: "flex",
              flexShrink: 0,
            }}
          >
            <Icon name={copied ? "check" : "copy"} size={12} />
          </button>
        )}
      </span>
    </div>
  );
}
