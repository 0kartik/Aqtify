import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import Logo from "../components/Logo.jsx";
import Icon from "../components/Icon.jsx";
import KeyBar from "../components/KeyBar.jsx";
import { API_DEFAULT, healthCheck } from "../api/client.js";

const TABS = [
  { id: "register", label: "Register", path: "/app/register" },
  { id: "bulk", label: "Bulk", path: "/app/bulk" },
  { id: "verify", label: "Verify", path: "/app/verify" },
  { id: "public", label: "Public Verify", path: "/app/public-verify" },
  { id: "history", label: "History", path: "/app/history" },
  { id: "review", label: "Review Queue", path: "/app/review" },
];

export default function AppLayout({ apiKey, setApiKey, children }) {
  const [status, setStatus] = useState("connecting…");
  const [theme, setTheme] = useState(localStorage.getItem("aqtify_theme") || "light");
  const apiBase = API_DEFAULT;
  const navigate = useNavigate();
  const location = useLocation();

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
          padding: "18px 32px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 16,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 12, textDecoration: "none", color: "var(--text)" }}>
            <Logo size={26} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
              <span style={{ fontSize: 19, fontWeight: 700, letterSpacing: "-0.01em" }}>Aqtify</span>
              <span
                style={{
                  fontSize: 11,
                  color: "var(--text-faint)",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                }}
              >
                PQ-SMAP Console
              </span>
            </div>
          </Link>
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
              onClick={() => navigate(t.path)}
              style={{
                flex: "1 1 120px",
                textAlign: "center",
                padding: "13px 10px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: 13.5,
                borderRight: "1px solid var(--border)",
                borderBottom: "1px solid var(--border)",
                background: location.pathname === t.path ? "var(--accent)" : "transparent",
                color: location.pathname === t.path ? "var(--accent-contrast)" : "var(--text-muted)",
                transition: "all .12s ease",
              }}
            >
              {t.label}
            </div>
          ))}
        </div>

        {children}
      </main>

      <footer style={{ textAlign: "center", color: "var(--text-faint)", fontSize: 11.5, padding: "0 20px 30px" }}>
        Aqtify · Post-Quantum Secure Media Authentication Protocol · API at{" "}
        <span className="mono">{apiBase}</span>
      </footer>
    </div>
  );
}