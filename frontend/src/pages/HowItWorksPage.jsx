const SECTIONS = [
  {
    title: "1. Registration",
    body: "When media is uploaded, Aqtify computes a cryptographic hash, embeds an imperceptible steganographic watermark directly into the file, and generates an ML-DSA-65 (CRYSTALS-Dilithium3) signature over the content. This is a post-quantum signature scheme — resistant to attacks from both classical and quantum computers, unlike RSA or ECDSA.",
  },
  {
    title: "2. AI-generation screening",
    body: "Before certification, the file is screened by a vision model trained to distinguish authentic camera-captured images from AI-generated or manipulated ones. The result — a confidence score and verdict — is attached to the certificate, not hidden after the fact.",
  },
  {
    title: "3. Certificate issuance",
    body: "A certificate is issued binding the file hash, signature, watermark reference, and AI-screening result together under a unique certificate ID. This certificate can be looked up independently of the original uploader.",
  },
  {
    title: "4. Verification",
    body: "Anyone with the file — or just the certificate ID — can verify authenticity: signature validity against the issuer's public key, hash match, embedded watermark integrity, and the AI-generation risk assessment, all in one lookup.",
  },
  {
    title: "5. Chain of custody",
    body: "Every verification event, re-check, and access is appended to an immutable custody log tied to the certificate, so the full history of who checked a file and when is auditable, not just the final verdict.",
  },
];

export default function HowItWorksPage() {
  return (
    <div style={{ maxWidth: 780, margin: "0 auto", padding: "72px 28px 96px" }}>
      <div
        className="mono"
        style={{
          fontSize: 11.5,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: "var(--text-muted)",
          marginBottom: 14,
        }}
      >
        Protocol
      </div>
      <h1 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.02em", margin: "0 0 16px" }}>
        How Aqtify works
      </h1>
      <p style={{ fontSize: 15.5, color: "var(--text-muted)", lineHeight: 1.65, marginBottom: 56 }}>
        Aqtify is a post-quantum secure media authentication protocol (PQ-SMAP). It combines
        cryptographic signing, steganographic watermarking, and AI-generation detection into a
        single certification pipeline — so authenticity can be verified independently of the
        platform, indefinitely.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
        {SECTIONS.map((s) => (
          <div key={s.title} style={{ borderTop: "1px solid var(--border)", paddingTop: 24 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 10px" }}>{s.title}</h2>
            <p style={{ fontSize: 14.5, color: "var(--text-muted)", lineHeight: 1.7, margin: 0 }}>{s.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}