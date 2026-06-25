import { useEffect, useState } from "react";
import Panel from "../components/Panel.jsx";
import Button from "../components/Button.jsx";
import ErrorBox from "../components/ErrorBox.jsx";
import Icon from "../components/Icon.jsx";
import { fetchMyRegistrations } from "../api/client.js";

const STATUS_TONE = {
  clear: { color: "var(--success)", bg: "var(--success-bg)", border: "var(--success-border)" },
  flagged: { color: "var(--warn)", bg: "var(--warn-bg)", border: "var(--warn-border)" },
  rejected: { color: "var(--danger)", bg: "var(--danger-bg)", border: "var(--danger-border)" },
  approved: { color: "var(--success)", bg: "var(--success-bg)", border: "var(--success-border)" },
};

export default function HistoryPanel({ apiBase, apiKey }) {
  const [records, setRecords] = useState(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  const load = async () => {
    setError("");
    if (!apiKey) return setError("Set an API key above first.");
    try {
      const data = await fetchMyRegistrations(apiBase, apiKey);
      setRecords(data.records);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  const filtered = (records || []).filter((r) => {
    const q = query.toLowerCase();
    return !q || r.certificate_id.toLowerCase().includes(q) || (r.file_name || "").toLowerCase().includes(q);
  });

  return (
    <Panel title="Registration history" subtitle="Everything registered with this API key.">
      <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by certificate ID or filename…"
          style={{
            flex: 1,
            minWidth: 220,
            background: "var(--surface)",
            border: "1px solid var(--border-strong)",
            borderRadius: 6,
            padding: "9px 12px",
            fontSize: 13,
            fontFamily: "var(--sans)",
          }}
        />
        <Button variant="secondary" onClick={load}>
          Refresh
        </Button>
      </div>

      <ErrorBox message={error} />

      {records && filtered.length === 0 && (
        <div style={{ fontSize: 13, color: "var(--text-muted)" }}>No registrations found.</div>
      )}

      {filtered.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {filtered.map((r) => {
            const tone = STATUS_TONE[r.review_status] || STATUS_TONE.clear;
            return (
              <div
                key={r.certificate_id}
                style={{
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  padding: "11px 14px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 10,
                  flexWrap: "wrap",
                  background: "var(--surface)",
                }}
              >
                <div>
                  <div className="mono" style={{ fontWeight: 600, fontSize: 13 }}>{r.certificate_id}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                    {r.file_name} · {r.media_type} · {new Date(r.created_at).toLocaleDateString()}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: tone.color,
                    background: tone.bg,
                    border: `1px solid ${tone.border}`,
                    padding: "4px 9px",
                    borderRadius: 5,
                    textTransform: "uppercase",
                    display: "flex",
                    alignItems: "center",
                    gap: 5,
                  }}
                >
                  <Icon name={r.review_status === "rejected" ? "x" : "check"} size={11} />
                  {r.review_status}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}
