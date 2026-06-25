export function openCertificatePdf({ certificateId, fileName, fileHash, algorithm, ownerName, mediaType, embedUrl }) {
  const qrSrc = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(embedUrl)}`;

  const html = `
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Aqtify Certificate — ${certificateId}</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, "Segoe UI", sans-serif;
    color: #1b1b18;
    padding: 48px;
    max-width: 720px;
    margin: 0 auto;
  }
  .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1b1b18; padding-bottom: 20px; margin-bottom: 28px; }
  .brand { font-size: 22px; font-weight: 700; }
  .brand small { display: block; font-size: 11px; letter-spacing: 0.08em; color: #726f68; text-transform: uppercase; font-weight: 500; margin-top: 2px; }
  .title { font-size: 15px; color: #726f68; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
  .cert-id { font-family: monospace; font-size: 20px; font-weight: 700; margin-bottom: 30px; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
  td { padding: 10px 0; border-bottom: 1px solid #e1e0da; font-size: 13px; }
  td:first-child { color: #726f68; width: 180px; }
  td:last-child { font-family: monospace; word-break: break-all; }
  .qr-block { text-align: center; margin-top: 20px; }
  .qr-block img { border: 1px solid #e1e0da; border-radius: 8px; }
  .qr-block p { font-size: 11px; color: #726f68; margin-top: 8px; }
  .footer { margin-top: 40px; font-size: 10.5px; color: #a6a49b; border-top: 1px solid #e1e0da; padding-top: 16px; }
  @media print { body { padding: 20px; } }
</style>
</head>
<body>
  <div class="header">
    <div class="brand">Aqtify<small>PQ-SMAP Authenticity Certificate</small></div>
  </div>

  <div class="title">Certificate ID</div>
  <div class="cert-id">${certificateId}</div>

  <table>
    <tr><td>File name</td><td>${fileName}</td></tr>
    <tr><td>Media type</td><td>${mediaType}</td></tr>
    <tr><td>File hash (SHA-256)</td><td>${fileHash}</td></tr>
    <tr><td>Signature algorithm</td><td>${algorithm}</td></tr>
    <tr><td>Owner</td><td>${ownerName || "—"}</td></tr>
    <tr><td>Issued</td><td>${new Date().toLocaleString()}</td></tr>
  </table>

  <div class="qr-block">
    <img src="${qrSrc}" width="180" height="180" alt="QR code">
    <p>Scan to verify this certificate publicly<br>${embedUrl}</p>
  </div>

  <div class="footer">
    This certificate attests that the above media was cryptographically signed with a
    post-quantum signature (ML-DSA-65 / CRYSTALS-Dilithium3) and watermarked at the time
    of registration. Verify at any time using the certificate ID above.
  </div>

  <script>window.onload = () => window.print();</script>
</body>
</html>`;

  const win = window.open("", "_blank");
  win.document.write(html);
  win.document.close();
}
