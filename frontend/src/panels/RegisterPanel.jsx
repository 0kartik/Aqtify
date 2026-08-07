import { useState, useEffect } from "react";
import Panel from "../components/Panel.jsx";
import Dropzone from "../components/Dropzone.jsx";
import Field from "../components/Field.jsx";
import { inputStyle } from "../styles.js";
import Pipeline from "../components/Pipeline.jsx";
import Button from "../components/Button.jsx";
import Icon from "../components/Icon.jsx";
import ErrorBox from "../components/ErrorBox.jsx";
import VerdictBanner from "../components/VerdictBanner.jsx";
import DataRow from "../components/DataRow.jsx";
import BeforeAfterSlider from "../components/BeforeAfterSlider.jsx";
import ReviewFlagModal from "../components/ReviewFlagModal.jsx";
import { registerMedia, downloadSecured } from "../api/client.js";
import { openCertificatePdf } from "../utils/certificatePdf.js";

const STEPS = ["Hash", "PQC Sign", "Watermark", "Registry"];

export default function RegisterPanel({ apiBase, apiKey }) {
  const [file, setFile] = useState(null);
  const [ownerName, setOwnerName] = useState("");
  const [ownerEmail, setOwnerEmail] = useState("");
  const [step, setStep] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [originalPreviewUrl, setOriginalPreviewUrl] = useState(null);
  const [showFlagModal, setShowFlagModal] = useState(false);

  const run = async () => {
    setError("");
    setResult(null);
    setDownloadUrl(null);
    setShowFlagModal(false);

    if (!file) return setError("Choose a file first.");
    if (!apiKey) return setError("Set an API key above first.");

    setBusy(true);
    for (let i = 0; i < STEPS.length; i++) {
      setStep(i);
      await new Promise((r) => setTimeout(r, 320));
    }
    setStep(STEPS.length);

    try {
      const isImage = file.type && file.type.startsWith("image/");
      if (isImage) setOriginalPreviewUrl(URL.createObjectURL(file));

      const data = await registerMedia(apiBase, apiKey, { file, ownerName, ownerEmail });
      setResult(data);
      const blob = await downloadSecured(apiBase, apiKey, data.certificate_id);
      setDownloadUrl(URL.createObjectURL(blob));

      // Fire the review pop-up immediately for flagged registrations,
      // rather than making the user notice a static banner or dig
      // through the review queue later.
      if (data.review_status === "flagged") {
        setShowFlagModal(true);
      }
    } catch (e) {
      setError(e.message || `Could not reach the API at ${apiBase}. Is the backend running?`);
    }
    setBusy(false);
    setStep(null);
  };

  const downloadCertificate = () => {
    openCertificatePdf({
      certificateId: result.certificate_id,
      fileName: file?.name || "media",
      fileHash: result.file_hash,
      algorithm: result.algorithm,
      ownerName,
      mediaType: result.media_type,
      embedUrl: `${apiBase}/embed/${result.certificate_id}`,
    });
  };

  return (
    <Panel
      title="Register media"
      subtitle="Signs the file with a post-quantum signature and embeds an invisible authenticity watermark. Supports images, WAV/audio, and video."
    >
      <Dropzone file={file} onFile={setFile} accept="image/*,audio/*,video/*" hint="JPG, PNG, WAV, MP3, MP4, MOV…" />

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 16 }}>
        <div style={{ flex: 1, minWidth: 180 }}>
          <Field label="Owner name (optional)">
            <input
              style={inputStyle}
              value={ownerName}
              onChange={(e) => setOwnerName(e.target.value)}
              placeholder="Jane Doe"
            />
          </Field>
        </div>
        <div style={{ flex: 1, minWidth: 180 }}>
          <Field label="Owner email (optional)">
            <input
              style={inputStyle}
              value={ownerEmail}
              onChange={(e) => setOwnerEmail(e.target.value)}
              placeholder="jane@example.com"
            />
          </Field>
        </div>
      </div>

      <Pipeline steps={STEPS} activeIndex={step} />
      <Button onClick={run} disabled={busy} style={{ width: "100%" }}>
        <Icon name="shield" size={15} /> Register media
      </Button>
      <ErrorBox message={error} />

      {result && (
        <div style={{ marginTop: 22 }}>
          <VerdictBanner
            tone={result.review_status === "flagged" ? "warn" : "ok"}
            score="✓"
            title={result.review_status === "flagged" ? "Registered — flagged for review" : "Registered"}
            subtitle={result.certificate_id}
          />

          {originalPreviewUrl && downloadUrl && (
            <BeforeAfterSlider beforeSrc={originalPreviewUrl} afterSrc={downloadUrl} />
          )}

          <div style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "4px 14px", marginTop: 14 }}>
            <DataRow k="certificate_id" v={result.certificate_id} copyable />
            <DataRow k="file_hash" v={result.file_hash} copyable />
            <DataRow k="media_type" v={result.media_type} />
            <DataRow k="algorithm" v={result.algorithm} />
            <DataRow k="key_mode" v={result.key_mode} />
            <DataRow k="watermark_embedded" v={result.watermark_embedded} />
            {result.ai_probability !== null && result.ai_probability !== undefined && (
              <DataRow k="ai_probability" v={`${result.ai_probability}%`} />
            )}
            <DataRow k="review_status" v={result.review_status} />
            {result.email && <DataRow k="email" v={result.email.sent ? "sent" : `not sent (${result.email.reason})`} />}
          </div>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
            {downloadUrl && (
              <a
                href={downloadUrl}
                download={result.certificate_id + (result.media_type === "audio" ? ".wav" : ".png")}
              >
                <Button variant="secondary">
                  <Icon name="download" size={14} /> Download secured file
                </Button>
              </a>
            )}
            <Button variant="ghost" onClick={downloadCertificate}>
              <Icon name="doc" size={14} /> Download certificate (PDF)
            </Button>
            {result.review_status === "flagged" && (
              <Button variant="ghost" onClick={() => setShowFlagModal(true)}>
                <Icon name="alert" size={14} /> View flag details
              </Button>
            )}
          </div>
        </div>
      )}

      {showFlagModal && (
        <ReviewFlagModal result={result} onDismiss={() => setShowFlagModal(false)} />
      )}
    </Panel>
  );
}