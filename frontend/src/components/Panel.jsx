export default function Panel({ title, subtitle, children }) {
  return (
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: 26,
        boxShadow: "0 1px 3px rgba(20,20,15,0.06), 0 8px 24px rgba(20,20,15,0.05)",
      }}
    >
      <h2 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 4px" }}>{title}</h2>
      <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20, lineHeight: 1.5 }}>
        {subtitle}
      </div>
      {children}
    </div>
  );
}
