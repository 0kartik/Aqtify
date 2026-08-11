import { Link } from "react-router-dom";
import Icon from "../components/Icon.jsx";

const FEATURES = [
  {
    icon: "shield",
    title: "Post-quantum signatures",
    body: "Every certificate is signed with ML-DSA-65 (CRYSTALS-Dilithium3), the NIST-standardized signature scheme built to resist attacks from quantum computers - not just today's threat model.",
  },
  {
    icon: "scan",
    title: "AI-generated image detection",
    body: "A dedicated vision model screens uploaded media for signs of AI generation or deepfake manipulation before it's certified, flagging risk rather than assuming trust.",
  },
  {
    icon: "doc",
    title: "Chain-of-custody logging",
    body: "Every verification, re-check, and access event is written to an immutable custody log tied to the certificate - a full audit trail, not just a pass/fail badge.",
  },
  {
    icon: "clock",
    title: "Steganographic watermarking",
    body: "An imperceptible watermark is embedded directly in the media, so authenticity travels with the file itself even outside the platform.",
  },
];

const TOOLS = [
  { path: "/app/register", icon: "upload", title: "Register", desc: "Sign and watermark a single file." },
  { path: "/app/bulk", icon: "layers", title: "Bulk register", desc: "Register many files at once." },
  { path: "/app/verify", icon: "scan", title: "Verify media", desc: "Check signature, watermark, and AI risk." },
  { path: "/app/public-verify", icon: "search", title: "Public verify", desc: "Look up a certificate, no key required." },
  { path: "/app/history", icon: "clock", title: "History", desc: "Past registrations and verifications." },
  { path: "/app/review", icon: "alert", title: "Review queue", desc: "Items flagged for manual review." },
];

const STEPS = [
  { n: "01", title: "Register", body: "Upload media. It's hashed, watermarked, and signed with a post-quantum key pair." },
  { n: "02", title: "Distribute", body: "The file carries its certificate ID and embedded watermark wherever it goes." },
  { n: "03", title: "Verify", body: "Anyone can check authenticity - signature validity, AI-generation risk, and custody history - in seconds." },
];

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: "88px 28px 96px",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.1fr 1fr",
            gap: 56,
            alignItems: "center",
          }}
          className="hero-grid"
        >
          {/* Left: copy */}
          <div>
            <div
              className="mono"
              style={{
                display: "inline-block",
                fontSize: 11.5,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: "var(--text-muted)",
                border: "1px solid var(--border-strong)",
                borderRadius: 999,
                padding: "6px 14px",
                marginBottom: 24,
              }}
            >
              PQ-SMAP · Post-Quantum Media Authentication
            </div>

            <h1
              style={{
                fontSize: "clamp(32px, 4.2vw, 50px)",
                fontWeight: 800,
                letterSpacing: "-0.02em",
                lineHeight: 1.1,
                margin: "0 0 20px",
              }}
            >
              Prove media is real.
              <br />
              Before it spreads.
            </h1>

            <p
              style={{
                fontSize: 16,
                color: "var(--text-muted)",
                maxWidth: 460,
                margin: "0 0 36px",
                lineHeight: 1.65,
              }}
            >
              Aqtify signs, watermarks, and screens media for AI generation at the point of
              creation - so authenticity can be verified independently, forever, even against
              quantum-capable adversaries.
            </p>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <Link
                to="/app/register"
                style={{
                  textDecoration: "none",
                  fontWeight: 700,
                  fontSize: 14.5,
                  padding: "13px 24px",
                  borderRadius: 7,
                  background: "var(--accent)",
                  color: "var(--accent-contrast)",
                }}
              >
                Register media
              </Link>
              <Link
                to="/app/public-verify"
                style={{
                  textDecoration: "none",
                  fontWeight: 700,
                  fontSize: 14.5,
                  padding: "13px 24px",
                  borderRadius: 7,
                  border: "1px solid var(--border-strong)",
                  color: "var(--text)",
                }}
              >
                Verify a certificate
              </Link>
            </div>
          </div>

          {/* Right: mock verification result card */}
          <div
            style={{
              border: "1px solid var(--border)",
              borderRadius: 14,
              background: "var(--surface)",
              padding: "22px 22px 20px",
              boxShadow: "0 20px 50px -20px rgba(0,0,0,0.35)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 18,
                paddingBottom: 16,
                borderBottom: "1px solid var(--border)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div
                  style={{
                    width: 22,
                    height: 22,
                    borderRadius: 6,
                    background: "var(--success-bg, rgba(34,197,94,0.15))",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Icon name="check" size={13} />
                </div>
                <span style={{ fontSize: 13.5, fontWeight: 700 }}>AUTHENTIC</span>
              </div>
              <span className="mono" style={{ fontSize: 10.5, color: "var(--text-faint)" }}>
                LOW RISK
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 18 }}>
              <ResultRow icon="key" label="Signature" value="Valid · ML-DSA-65" ok />
              <ResultRow icon="doc" label="Watermark" value="Intact" ok />
              <ResultRow icon="scan" label="AI-generation risk" value="4.2%" ok />
              <ResultRow icon="clock" label="Custody events" value="3 logged" />
            </div>

            <div
              className="mono"
              style={{
                fontSize: 10.5,
                color: "var(--text-faint)",
                background: "var(--surface-alt)",
                border: "1px solid var(--border)",
                borderRadius: 6,
                padding: "8px 10px",
                overflowWrap: "anywhere",
              }}
            >
              AUTH-7F2C91D0B4E6
            </div>
          </div>
        </div>
      </section>


      {/* Feature grid */}
      <section style={{ background: "var(--surface)", borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
        <div style={{ maxWidth: 1120, margin: "0 auto", padding: "64px 28px" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
              gap: 28,
            }}
          >
            {FEATURES.map((f) => (
              <div key={f.title}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 8,
                    background: "var(--surface-alt)",
                    border: "1px solid var(--border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: 14,
                  }}
                >
                  <Icon name={f.icon} size={18} />
                </div>
                <h3 style={{ fontSize: 15.5, fontWeight: 700, margin: "0 0 8px" }}>{f.title}</h3>
                <p style={{ fontSize: 13.5, color: "var(--text-muted)", lineHeight: 1.6, margin: 0 }}>{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tools — direct links into each page */}
      <section style={{ maxWidth: 1120, margin: "0 auto", padding: "72px 28px 80px" }}>
        <h2 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.01em", marginBottom: 8, textAlign: "center" }}>
          Jump to a tool
        </h2>
        <p style={{ fontSize: 13.5, color: "var(--text-muted)", textAlign: "center", marginBottom: 32 }}>
          No account needed to try registration or verification.
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 16,
          }}
        >
          {TOOLS.map((tool) => (
            <Link
              key={tool.path}
              to={tool.path}
              style={{
                textDecoration: "none",
                color: "inherit",
                display: "flex",
                alignItems: "flex-start",
                gap: 14,
                border: "1px solid var(--border)",
                borderRadius: 10,
                padding: "20px 20px",
                background: "var(--surface)",
                transition: "border-color .15s ease, transform .15s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--accent)";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--border)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div
                style={{
                  width: 38,
                  height: 38,
                  flexShrink: 0,
                  borderRadius: 8,
                  background: "var(--surface-alt)",
                  border: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Icon name={tool.icon} size={17} />
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 14.5, fontWeight: 700, marginBottom: 4 }}>{tool.title}</div>
                <div style={{ fontSize: 12.5, color: "var(--text-muted)", lineHeight: 1.5 }}>{tool.desc}</div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* How it works strip */}
      <section style={{ maxWidth: 1120, margin: "0 auto", padding: "72px 28px" }}>
        <h2 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.01em", marginBottom: 40, textAlign: "center" }}>
          How it works
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 32 }}>
          {STEPS.map((s) => (
            <div key={s.n}>
              <div
                className="mono"
                style={{ fontSize: 13, color: "var(--text-faint)", marginBottom: 8, fontWeight: 700 }}
              >
                {s.n}
              </div>
              <h3 style={{ fontSize: 16.5, fontWeight: 700, margin: "0 0 8px" }}>{s.title}</h3>
              <p style={{ fontSize: 13.5, color: "var(--text-muted)", lineHeight: 1.6, margin: 0 }}>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA band */}
      <section style={{ background: "var(--accent)", color: "var(--accent-contrast)" }}>
        <div
          style={{
            maxWidth: 1120,
            margin: "0 auto",
            padding: "56px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 20,
          }}
        >
          <div>
            <h2 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 6px" }}>Start authenticating media</h2>
            <p style={{ fontSize: 14, opacity: 0.8, margin: 0 }}>No signup required to try a verification.</p>
          </div>
          <Link
            to="/app/register"
            style={{
              textDecoration: "none",
              fontWeight: 700,
              fontSize: 14.5,
              padding: "13px 26px",
              borderRadius: 7,
              background: "var(--accent-contrast)",
              color: "var(--accent)",
            }}
          >
            Open the console →
          </Link>
        </div>
      </section>

      <style>{`
        @media (max-width: 860px) {
          .hero-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

function ResultRow({ icon, label, value, ok }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)" }}>
        <Icon name={icon} size={14} />
        <span style={{ fontSize: 12.5 }}>{label}</span>
      </div>
      <span
        className="mono"
        style={{
          fontSize: 12,
          fontWeight: 600,
          color: ok ? "var(--success, #22c55e)" : "var(--text)",
        }}
      >
        {value}
      </span>
    </div>
  );
}