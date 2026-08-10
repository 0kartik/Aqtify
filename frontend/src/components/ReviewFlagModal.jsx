import Icon from "./Icon.jsx";
import Button from "./Button.jsx";
import { Link } from "react-router-dom";

export default function ReviewFlagModal({ result, onDismiss }) {
  if (!result || result.review_status !== "flagged") return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        padding: 20,
      }}
      onClick={onDismiss}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "var(--surface)",
          border: "1px solid var(--warn-border)",
          borderRadius: 12,
          padding: "26px 26px 22px",
          maxWidth: 440,
          width: "100%",
          boxShadow: "0 24px 60px -20px rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 16 }}>
          <div
            style={{
              width: 40,
              height: 40,
              flexShrink: 0,
              borderRadius: 8,
              background: "var(--warn-bg)",
              border: "1px solid var(--warn-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon name="alert" size={19} />
          </div>
          <div>
            <div style={{ fontSize: 16.5, fontWeight: 700, marginBottom: 4 }}>
              Flagged for human review
            </div>
            <div style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.55 }}>
              This file registered successfully, but the AI-detection ensemble scored it{" "}
              <strong style={{ color: "var(--text)" }}>{result.ai_probability}%</strong> AI-generation
              probability — high enough to flag, not high enough to block automatically.
            </div>
          </div>
        </div>

        <div
          style={{
            border: "1px solid var(--border)",
            borderRadius: 8,
            padding: "12px 14px",
            marginBottom: 18,
            fontSize: 12.5,
            color: "var(--text-muted)",
            lineHeight: 1.6,
          }}
        >
          The certificate is issued, but marked <span className="mono">review_status: flagged</span>{" "}
          until a human confirms it in the review queue. This is by design — no single AI-detection
          model is fully reliable, so borderline cases go to a person instead of an automatic reject.
        </div>

        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <Button variant="ghost" onClick={onDismiss}>
            Dismiss
          </Button>
          <Link to="/app/review" style={{ textDecoration: "none" }}>
            <Button variant="primary">
              <Icon name="alert" size={14} /> Open review queue
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}