import { Link } from "react-router-dom";
import Logo from "../components/Logo.jsx";
import Icon from "../components/Icon.jsx";
import KeyBar from "../components/KeyBar.jsx";
import { useEffect, useState } from "react";
import { API_DEFAULT, healthCheck } from "../api/client.js";

/**
 * StandalonePage: wraps a single console panel with no persistent
 * cross-page nav. Just a small back-to-console link, the page's own
 * identity (title/icon), and the API key bar (needed on every page
 * that talks to the backend).
 */
export default function StandalonePage({ title, apiKey, setApiKey, children }) {
  const [status, setStatus] = useState("connecting…");
  const [online, setOnline] = useState(null);
  const [theme, setTheme] = useState(localStorage.getItem("aqtify_theme") || "light");
  const apiBase = API_DEFAULT;

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("aqtify_theme", theme);
  }, [theme]);

  useEffect(() => {
    healthCheck(apiBase)
      .then((d) => {
        setStatus(d.algorithm || "ML-DSA-65");
        setOnline(true);
      })
      .catch(() => {
        setStatus("API offline");
        setOnline(false);
      });
  }, [apiBase]);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header
        style={{
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          padding: "16px 32px",
        }}
      >
        <div
          style={{
            maxWidth: 760,
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <Link
            to="/app"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              textDecoration: "none",
              color: "var(--text-muted)",
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            <Icon name="x" size={13} />
            Console
          </Link>

          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: online === false ? "var(--danger)" : online ? "var(--success)" : "var(--text-faint)",
              }}
            />
            <span className="mono" style={{ fontSize: 10.5, color: "var(--text-muted)" }}>
              {status}
            </span>
            <button
              type="button"
              onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
              title="Toggle theme"
              style={{
                border: "1px solid var(--border-strong)",
                background: "var(--surface-alt)",
                borderRadius: 6,
                padding: 6,
                cursor: "pointer",
                color: "var(--text-muted)",
                display: "flex",
              }}
            >
              <Icon name={theme === "light" ? "moon" : "sun"} size={13} />
            </button>
          </div>
        </div>
      </header>

      <div style={{ borderBottom: "1px solid var(--border)", background: "var(--surface)", padding: "10px 32px" }}>
        <div style={{ maxWidth: 760, margin: "0 auto" }}>
          <KeyBar apiBase={apiBase} apiKey={apiKey} onChange={setApiKey} />
        </div>
      </div>

      <main style={{ flex: 1, padding: "40px 32px 80px" }}>
        <div style={{ maxWidth: 760, margin: "0 auto" }}>{children}</div>
      </main>
    </div>
  );
}