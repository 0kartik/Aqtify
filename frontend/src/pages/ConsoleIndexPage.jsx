import { Link } from "react-router-dom";
import Icon from "../components/Icon.jsx";
import Logo from "../components/Logo.jsx";

const TOOLS = [
  {
    section: "Certify",
    items: [
      { path: "/app/register", icon: "upload", title: "Register", desc: "Sign and watermark a single file." },
      { path: "/app/bulk", icon: "layers", title: "Bulk register", desc: "Register many files at once." },
    ],
  },
  {
    section: "Verify",
    items: [
      { path: "/app/verify", icon: "scan", title: "Verify media", desc: "Check signature, watermark, and AI-generation risk." },
      { path: "/app/public-verify", icon: "search", title: "Public verify", desc: "Look up a certificate by ID, no key required." },
    ],
  },
  {
    section: "Manage",
    items: [
      { path: "/app/history", icon: "clock", title: "History", desc: "Your past registrations and verifications." },
      { path: "/app/review", icon: "alert", title: "Review queue", desc: "Items flagged for manual review." },
    ],
  },
];

export default function ConsoleIndexPage() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <header
        style={{
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          padding: "18px 32px",
        }}
      >
        <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", alignItems: "center", gap: 12 }}>
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", color: "var(--text)" }}>
            <Logo size={24} />
            <span style={{ fontWeight: 700, fontSize: 17 }}>Aqtify</span>
          </Link>
          <span style={{ fontSize: 11, color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Console
          </span>
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: "0 auto", padding: "48px 32px 80px" }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.01em", marginBottom: 6 }}>Console</h1>
        <p style={{ fontSize: 14, color: "var(--text-muted)", marginBottom: 40 }}>
          Choose a tool to open.
        </p>

        {TOOLS.map((group) => (
          <div key={group.section} style={{ marginBottom: 36 }}>
            <div
              style={{
                fontSize: 11,
                fontWeight: 700,
                color: "var(--text-faint)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                marginBottom: 12,
              }}
            >
              {group.section}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 14 }}>
              {group.items.map((tool) => (
                <Link
                  key={tool.path}
                  to={tool.path}
                  style={{
                    textDecoration: "none",
                    color: "inherit",
                    display: "block",
                    border: "1px solid var(--border)",
                    borderRadius: 10,
                    padding: "18px 18px",
                    background: "var(--surface)",
                    transition: "border-color .12s ease",
                  }}
                >
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 7,
                      background: "var(--surface-alt)",
                      border: "1px solid var(--border)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginBottom: 12,
                    }}
                  >
                    <Icon name={tool.icon} size={16} />
                  </div>
                  <div style={{ fontSize: 14.5, fontWeight: 700, marginBottom: 4 }}>{tool.title}</div>
                  <div style={{ fontSize: 12.5, color: "var(--text-muted)", lineHeight: 1.5 }}>{tool.desc}</div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}