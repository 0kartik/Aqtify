import { useState } from "react";
import Panel from "../components/Panel.jsx";
import Dropzone from "../components/Dropzone.jsx";
import Field from "../components/Field.jsx";
import { inputStyle } from "../styles.js";
import Pipeline from "../components/Pipeline.jsx";
import Button from "../components/Button.jsx";
import Icon from "../components/Icon.jsx";
import ErrorBox from "../components/ErrorBox.jsx";
import VerdictBanner from "../components/VerdictBanner.jsx";
import CheckGrid from "../components/CheckGrid.jsx";
import DataRow from "../components/DataRow.jsx";
import { verifyMedia, fetchManifest, fetchCustodyLog } from "../api/client.js";

const STEPS = ["Extract", "Hash Check", "Signature", "AI Scan", "Score"];

export default function VerifyPanel({ apiBase, apiKey }) {
  const [file, setFile] = useState(null);
  const [certId, setCertId] = useState("");
  const [step, setStep] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [extraTitle, setExtraTitle] = useState("");
  const [extraContent, setExtraContent] = useState("");

  const run = async () => {
    setError("");
    setResult(null);
    setExtraContent("");

    if (!file) return setError("Choose a file first.");
    if (!apiKey) return setError("Set an API key above first.");

    setBusy(true);
    for (let i = 0; i < STEPS.length; i++) {
      setStep(i);
      await new Promise((r) => setTimeout(r, 280));
    }
    setStep(STEPS.length);

    try {
      const data = await verifyMedia(apiBase, apiKey, { file, certificateId: certId });
      setResult(data);
    } catch (e) {
      setError(e.message || `Could not reach the API at ${apiBase}. Is the backend running?`);
    }
    setBusy(false);
    setStep(null);
  };

  const loadExtra = async (kind) => {
    if (!result) return;
    setExtraTitle(kind === "manifest" ? "C2PA-inspired manifest" : "Chain of custody");
    setExtraContent("Loading…");
    try {
      const data =
        kind === "manifest"
          ? await fetchManifest(apiBase, apiKey, result.certificate_id)
          : await fetchCustodyLog(apiBase, apiKey, result.certificate_id);
      setExtraContent(JSON.stringify(data, null, 2));
    } catch {
      setExtraContent("Could not load.");
    }
  };

  const tone = result
    ? result.overall_status === "AUTHENTIC"
      ? "ok"
      : result.risk_level === "MEDIUM RISK"
        ? "warn"
        : "bad"
    : "ok";

  return (
    <Panel
      title="Verify media"
      subtitle="Extracts the watermark, checks the post-quantum signature against the registry, and flags tampering."
    >
      <Dropzone file={file} onFile={setFile} accept="image/*,audio/*,video/*" hint="Use the file returned by Register" />

      <Field label="Certificate ID (optional — used if watermark can't be read)">
        <input
          style={inputStyle}
          className="mono"
          value={certId}
          onChange={(e) => setCertId(e.target.value)}
          placeholder="AUTH-XXXXXXXXXX"
        />
      </Field>

      <Pipeline steps={STEPS} activeIndex={step} />
      <Button onClick={run} disabled={busy} style={{ width: "100%" }}>
        <Icon name="scan" size={15} /> Verify media
      </Button>
      <ErrorBox message={error} />

      {result && (
        <div style={{ marginTop: 22 }}>
          <VerdictBanner
            tone={tone}
            score={result.authenticity_score}
            title={result.overall_status}
            subtitle={`${result.risk_level} · certificate ${result.certificate_id}`}
          />
          <CheckGrid checks={result.checks} />
          <div style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "4px 14px", marginBottom: 16 }}>
            <DataRow k="certificate_id" v={result.certificate_id} copyable />
            <DataRow k="file_hash" v={result.file_hash} copyable />
            <DataRow k="owner" v={result.owner || "—"} />
            <DataRow k="key_mode" v={result.key_mode} />
            <DataRow k="ai_probability" v={(result.ai_analysis.ai_probability ?? "n/a") + "%"} />
            <DataRow k="timestamp" v={result.timestamp} />
          </div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Button variant="ghost" onClick={() => loadExtra("manifest")}>
              <Icon name="doc" size={14} /> View manifest
            </Button>
            <Button variant="ghost" onClick={() => loadExtra("custody")}>
              <Icon name="clock" size={14} /> View custody log
            </Button>
          </div>
          {extraContent && (
            <div style={{ marginTop: 14 }}>
              <div
                style={{
                  fontSize: 11.5,
                  fontWeight: 600,
                  color: "var(--text-muted)",
                  textTransform: "uppercase",
                  marginBottom: 6,
                }}
              >
                {extraTitle}
              </div>
              <pre
                className="mono"
                style={{
                  background: "var(--surface-alt)",
                  border: "1px solid var(--border)",
                  borderRadius: 6,
                  padding: 14,
                  fontSize: 11.5,
                  overflowX: "auto",
                  maxHeight: 320,
                  overflowY: "auto",
                }}
              >
                {extraContent}
              </pre>
            </div>
          )}
        </div>
      )}
    </Panel>
  );
}
