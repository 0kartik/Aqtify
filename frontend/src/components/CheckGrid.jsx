import Icon from "./Icon.jsx";

export default function CheckGrid({ checks }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(150px,1fr))",
        gap: 8,
        marginBottom: 16,
      }}
    >
      {Object.entries(checks).map(([k, v]) => (
        <div
          key={k}
          style={{
            border: "1px solid var(--border)",
            borderRadius: 6,
            padding: "9px 12px",
            fontSize: 12,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "var(--surface)",
          }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 7, color: "var(--text-muted)" }}>
            <span style={{ color: v ? "var(--success)" : "var(--danger)" }}>
              <Icon name={v ? "check" : "x"} size={13} />
            </span>
            {k.replace(/_/g, " ")}
          </span>
          <b style={{ color: v ? "var(--success)" : "var(--danger)" }}>{v ? "PASS" : "FAIL"}</b>
        </div>
      ))}
    </div>
  );
}
