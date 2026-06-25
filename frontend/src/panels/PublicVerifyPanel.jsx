import { useState } from "react";
import Panel from "../components/Panel.jsx";
import Button from "../components/Button.jsx";
import Icon from "../components/Icon.jsx";
import ErrorBox from "../components/ErrorBox.jsx";
import DataRow from "../components/DataRow.jsx";
import VerdictBanner from "../components/VerdictBanner.jsx";
import { publicVerify, badgeUrl } from "../api/client.js";

export default function PublicVerifyPanel({ apiBase }) {
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const search = async () => {
    setError("");
    setResult(null);
    if (!query.trim()) return setError("Enter a certificate ID or file hash.");

    setBusy(true);
    try {
      const isCert = query.trim().toUpperCase().startsWith("AUTH-");
      const data = await publicVerify(apiBase, isCert ? { certificateId: query.trim() } : { hash: query.trim() });
      setResult(data);
    } catch (e) {
      setError(e.message || "No matching record found.");
    }
    setBusy(false);
  };

  return (
    <Panel
      title="Public verification"
      subtitle="Anyone can check a claim here — no account or API key needed. Only non-sensitive fields are shown."
    >
      <div style={{ display: "flex", gap: 10 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="AUTH-XXXXXXXXXX or a file hash"
          className="mono"
          style={{
            flex: 1,
            background: "var(--surface)",
            border: "1px solid var(--border-strong)",
            borderRadius: 6,
            padding: "10px 12px",
            fontSize: 13,
          }}
        />
        <Button onClick={search} disabled={busy}>
          <Icon name="search" size={14} /> Verify
        </Button>
      </div>

      <ErrorBox message={error} />

      {result && (
        <div style={{ marginTop: 22 }}>
          <VerdictBanner
            tone={result.verification_status === "AUTHENTIC" ? "ok" : "bad"}
            score={result.verification_status === "AUTHENTIC" ? "✓" : "✕"}
            title={result.verification_status}
            subtitle={result.certificate_id}
          />
          <div style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "4px 14px", marginBottom: 14 }}>
            <DataRow k="file_name" v={result.file_name} />
            <DataRow k="media_type" v={result.media_type} />
            <DataRow k="owner_name" v={result.owner_name || "—"} />
            <DataRow k="algorithm" v={result.algorithm} />
            <DataRow k="registered" v={new Date(result.created_at).toLocaleString()} />
          </div>
          <img src={badgeUrl(apiBase, result.certificate_id)} alt="status badge" />
        </div>
      )}
    </Panel>
  );
}
