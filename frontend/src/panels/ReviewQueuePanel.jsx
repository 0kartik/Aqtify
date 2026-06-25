import { useEffect, useState } from "react";
import Panel from "../components/Panel.jsx";
import Button from "../components/Button.jsx";
import ErrorBox from "../components/ErrorBox.jsx";

export default function ReviewQueuePanel({ apiBase, apiKey }) {
  const [queue, setQueue] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    setError("");
    if (!apiKey) return setError("Set an API key above first.");
    try {
      const res = await fetch(`${apiBase}/api/review-queue?status=pending`, {
        headers: { "X-API-Key": apiKey },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Could not load review queue.");
      setQueue(data.queue);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  const resolve = async (certificateId, decision) => {
    try {
      const form = new FormData();
      form.append("decision", decision);
      const res = await fetch(`${apiBase}/api/review-queue/${certificateId}/resolve`, {
        method: "POST",
        body: form,
        headers: { "X-API-Key": apiKey },
      });
      if (!res.ok) throw new Error("Could not resolve.");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Panel
      title="Review queue"
      subtitle="Registrations flagged by the AI-detection gate (above the flag threshold but below the block threshold) — approve or reject manually."
    >
      <Button variant="secondary" onClick={load} style={{ marginBottom: 16 }}>
        Refresh
      </Button>
      <ErrorBox message={error} />

      {queue && queue.length === 0 && (
        <div style={{ fontSize: 13, color: "var(--text-muted)" }}>Nothing pending review.</div>
      )}

      {queue && queue.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {queue.map((item) => (
            <div
              key={item.certificate_id}
              style={{
                border: "1px solid var(--warn-border)",
                background: "var(--warn-bg)",
                borderRadius: 8,
                padding: "12px 14px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: 10,
              }}
            >
              <div>
                <div className="mono" style={{ fontWeight: 600, fontSize: 13 }}>{item.certificate_id}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                  AI probability: {item.ai_probability}% · {item.reason}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <Button variant="secondary" onClick={() => resolve(item.certificate_id, "approved")}>
                  Approve
                </Button>
                <Button variant="ghost" onClick={() => resolve(item.certificate_id, "rejected")}>
                  Reject
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}
