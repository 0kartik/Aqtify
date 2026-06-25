import { useEffect, useState } from "react";
import Logo from "./components/Logo.jsx";
import Icon from "./components/Icon.jsx";
import KeyBar from "./components/KeyBar.jsx";
import RegisterPanel from "./panels/RegisterPanel.jsx";
import BulkRegisterPanel from "./panels/BulkRegisterPanel.jsx";
import VerifyPanel from "./panels/VerifyPanel.jsx";
import PublicVerifyPanel from "./panels/PublicVerifyPanel.jsx";
import HistoryPanel from "./panels/HistoryPanel.jsx";
import ReviewQueuePanel from "./panels/ReviewQueuePanel.jsx";
import { API_DEFAULT, healthCheck } from "./api/client.js";

const TABS = [
  { id: "register", label: "Register" },
  { id: "bulk", label: "Bulk" },
  { id: "verify", label: "Verify" },
  { id: "public", label: "Public Verify" },
  { id: "history", label: "History" },
  { id: "review", label: "Review Queue" },
];

export default function App() {
  const [tab, setTab] = useState("register");
  const [apiKey, setApiKey] = useState(localStorage.getItem("aqtify_api_key") || "");
  const [status, setStatus] = useState("connecting…");
  const [theme, setTheme] = useState(localStorage.getItem("aqtify_theme") || "light");
  const apiBase = API_DEFAULT;

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("aqtify_theme", theme);
  }, [theme]);

  useEffect(() => {
    healthCheck(apiBase)
      .then((d) => setStatus(`${d.algorithm || "ML-DSA-65"} · online`))
      .catch(() => setStatus("API offline — start the backend"));
  }, [apiBase]);

  return (
    <div>
      <header
        style={{
          padding: "26px 32px 20px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 16,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Logo size={28} />
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: "-0.01em" }}>Aqtify</h1>
            <span
              style={{
                fontSize: 11.5,
                color: "var(--text-faint)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
              }}
            >
              PQ-SMAP Console
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            className="mono"
            style={{
              fontSize: 11,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              color: "var(--text-muted)",
              border: "1px solid var(--border-strong)",
              padding: "5px 10px",
              borderRadius: 5,
              background: "var(--surface-alt)",
            }}
          >
            {status}
          </div>
          <button
            type="button"
            onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
            title="Toggle theme"
            style={{
              border: "1px solid var(--border-strong)",
              background: "var(--surface-alt)",
              borderRadius: 6,
              padding: 7,
              cursor: "pointer",
              color: "var(--text-muted)",
              display: "flex",
            }}
          >
            <Icon name={theme === "light" ? "moon" : "sun"} size={14} />
          </button>
        </div>
      </header>

      <KeyBar apiBase={apiBase} apiKey={apiKey} onChange={setApiKey} />

      <main style={{ maxWidth: 920, margin: "0 auto", padding: "24px 24px 80px" }}>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            border: "1px solid var(--border)",
            borderRadius: 10,
            overflow: "hidden",
            marginBottom: 22,
            background: "var(--surface)",
          }}
        >
          {TABS.map((t) => (
            <div
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                flex: "1 1 120px",
                textAlign: "center",
                padding: "13px 10px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: 13.5,
                borderRight: "1px solid var(--border)",
                borderBottom: "1px solid var(--border)",
                background: tab === t.id ? "var(--accent)" : "transparent",
                color: tab === t.id ? "var(--accent-contrast)" : "var(--text-muted)",
                transition: "all .12s ease",
              }}
            >
              {t.label}
            </div>
          ))}
        </div>

        {tab === "register" && <RegisterPanel apiBase={apiBase} apiKey={apiKey} />}
        {tab === "bulk" && <BulkRegisterPanel apiBase={apiBase} apiKey={apiKey} />}
        {tab === "verify" && <VerifyPanel apiBase={apiBase} apiKey={apiKey} />}
        {tab === "public" && <PublicVerifyPanel apiBase={apiBase} />}
        {tab === "history" && <HistoryPanel apiBase={apiBase} apiKey={apiKey} />}
        {tab === "review" && <ReviewQueuePanel apiBase={apiBase} apiKey={apiKey} />}
      </main>

      <footer style={{ textAlign: "center", color: "var(--text-faint)", fontSize: 11.5, padding: "0 20px 30px" }}>
        Aqtify · Post-Quantum Secure Media Authentication Protocol · API at{" "}
        <span className="mono">{apiBase}</span>
      </footer>
    </div>
  );
}
