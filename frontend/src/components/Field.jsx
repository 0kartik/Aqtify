export default function Field({ label, children, hint }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label
        style={{
          display: "block",
          fontSize: 11.5,
          fontWeight: 600,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.04em",
          marginBottom: 6,
        }}
      >
        {label}
      </label>
      {children}
      {hint && (
        <div style={{ fontSize: 11.5, color: "var(--text-faint)", marginTop: 4 }}>{hint}</div>
      )}
    </div>
  );
}
