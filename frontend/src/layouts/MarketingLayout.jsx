import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Logo from "../components/Logo.jsx";
import Icon from "../components/Icon.jsx";

const NAV_LINKS = [
  { to: "/", label: "Overview" },
  { to: "/how-it-works", label: "How it works" },
  { to: "/app/verify", label: "Verify a file" },
];

export default function MarketingLayout({ children }) {
  const location = useLocation();
  const [theme, setTheme] = useState(localStorage.getItem("aqtify_theme") || "light");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("aqtify_theme", theme);
  }, [theme]);

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 20,
          background: "var(--surface)",
          borderBottom: "1px solid var(--border)",
          backdropFilter: "blur(6px)",
        }}
      >
        <div
          style={{
            maxWidth: 1120,
            margin: "0 auto",
            padding: "16px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Link
            to="/"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
              color: "var(--text)",
            }}
          >
            <Logo size={26} />
            <span style={{ fontWeight: 700, fontSize: 18, letterSpacing: "-0.01em" }}>Aqtify</span>
          </Link>

          <nav style={{ display: "flex", alignItems: "center", gap: 28 }}>
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                style={{
                  textDecoration: "none",
                  fontSize: 13.5,
                  fontWeight: 600,
                  color: location.pathname === link.to ? "var(--text)" : "var(--text-muted)",
                }}
              >
                {link.label}
              </Link>
            ))}
            <Link
              to="/app"
              style={{
                textDecoration: "none",
                fontSize: 13.5,
                fontWeight: 700,
                padding: "9px 16px",
                borderRadius: 6,
                background: "var(--accent)",
                color: "var(--accent-contrast)",
              }}
            >
              Open console
            </Link>
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
          </nav>
        </div>
      </header>

      <main style={{ flex: 1 }}>{children}</main>

      <footer
        style={{
          borderTop: "1px solid var(--border)",
          padding: "36px 28px",
          background: "var(--surface)",
        }}
      >
        <div
          style={{
            maxWidth: 1120,
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)", fontSize: 12.5 }}>
            <Logo size={16} />
            <span>Aqtify · Post-Quantum Secure Media Authentication Protocol</span>
          </div>
          <div style={{ display: "flex", gap: 20, fontSize: 12.5, color: "var(--text-faint)" }}>
            <Link to="/how-it-works" style={{ color: "inherit", textDecoration: "none" }}>
              How it works
            </Link>
            <Link to="/app/public-verify" style={{ color: "inherit", textDecoration: "none" }}>
              Public verify
            </Link>
            <a
              href="https://github.com/0kartik"
              target="_blank"
              rel="noreferrer"
              style={{ color: "inherit", textDecoration: "none" }}
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}