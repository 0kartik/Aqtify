export default function AIDetectionBreakdown({ analysis }) {
  if (!analysis) return null;

  const { supported, ai_probability, confidence, verdict, model_name, error } = analysis;

  if (!supported) {
    return (
      <div
        style={{
          border: "1px solid var(--warn-border)",
          background: "var(--warn-bg)",
          borderRadius: 8,
          padding: "12px 16px",
          marginTop: 12,
          marginBottom: 16,
          fontSize: 12.5,
          color: "var(--warn)",
        }}
      >
        AI-detection unavailable — {error || "model not loaded."}
      </div>
    );
  }

  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: 8,
        padding: "14px 16px",
        marginTop: 12,
        marginBottom: 16,
        background: "var(--surface)",
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.03em",
          marginBottom: 10,
        }}
      >
        AI-generated image analysis
      </div>

      <div style={{ display: "flex", gap: 28, flexWrap: "wrap", alignItems: "baseline" }}>
        <div>
          <div style={{ fontSize: 10.5, color: "var(--text-muted)", marginBottom: 4 }}>AI probability</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: "var(--accent)" }}>{ai_probability}%</div>
        </div>
        <div>
          <div style={{ fontSize: 10.5, color: "var(--text-muted)", marginBottom: 4 }}>Model confidence</div>
          <div style={{ fontSize: 17, fontWeight: 700 }}>{confidence ?? "—"}%</div>
        </div>
        <div>
          <div style={{ fontSize: 10.5, color: "var(--text-muted)", marginBottom: 4 }}>Verdict</div>
          <div style={{ fontSize: 13.5, fontWeight: 600 }}>{verdict}</div>
        </div>
      </div>

      {model_name && (
        <div className="mono" style={{ fontSize: 10.5, color: "var(--text-faint)", marginTop: 10 }}>
          model: {model_name}
        </div>
      )}
    </div>
  );
}