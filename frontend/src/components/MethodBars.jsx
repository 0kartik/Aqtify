export default function MethodBars({ methods }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(190px,1fr))",
        gap: 10,
        marginTop: 16,
      }}
    >
      {Object.entries(methods).map(([k, v]) => (
        <div
          key={k}
          style={{
            border: "1px solid var(--border)",
            borderRadius: 6,
            padding: "10px 12px",
            background: "var(--surface)",
          }}
        >
          <div
            style={{
              fontSize: 11,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.03em",
              marginBottom: 7,
            }}
          >
            {k.replace(/_/g, " ")}
          </div>
          <div style={{ height: 6, borderRadius: 3, background: "var(--surface-alt)", overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${v}%`, background: "var(--accent)" }} />
          </div>
          <div style={{ fontSize: 12.5, marginTop: 6, fontWeight: 600 }}>{v}%</div>
        </div>
      ))}
    </div>
  );
}
