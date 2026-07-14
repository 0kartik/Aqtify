const DEFAULT_API_BASE = "http://127.0.0.1:8000";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "aqtify-verify-image",
    title: "Verify with Aqtify (PQ-SMAP)",
    contexts: ["image"],
  });
});

async function getSettings() {
  const stored = await chrome.storage.local.get(["apiBase", "apiKey"]);
  return {
    apiBase: stored.apiBase || DEFAULT_API_BASE,
    apiKey: stored.apiKey || "",
  };
}

function notify(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon48.png",
    title,
    message,
  });
}

chrome.contextMenus.onClicked.addListener(async (info) => {
  if (info.menuItemId !== "aqtify-verify-image" || !info.srcUrl) return;

  const { apiBase, apiKey } = await getSettings();
  if (!apiKey) {
    notify("Aqtify", "Set an API key in the extension popup first.");
    return;
  }

  try {
    // Fetching the image bytes only works if the host allows cross-origin
    // reads (or the image is same-origin). This is an inherent browser
    // limitation for a client-side extension, not an Aqtify limitation.
    const imgRes = await fetch(info.srcUrl);
    if (!imgRes.ok) throw new Error("Could not fetch the image (status " + imgRes.status + ")");
    const blob = await imgRes.blob();

    const form = new FormData();
    form.append("file", blob, "image.png");

    const res = await fetch(apiBase + "/api/verify", {
      method: "POST",
      headers: { "X-API-Key": apiKey },
      body: form,
    });
    const data = await res.json();

    if (!res.ok) {
      notify("Aqtify — request failed", data.detail || "Unknown error");
      return;
    }
    if (data.status === "not_found") {
      notify("Aqtify — not registered", "No authenticity record found for this image.");
      return;
    }

    notify(
      "Aqtify — " + data.overall_status,
      `Score ${data.authenticity_score}/100 · ${data.risk_level} · cert ${data.certificate_id}`
    );
  } catch (e) {
    notify("Aqtify — error", e.message || "Could not reach the API or fetch the image (CORS?).");
  }
});
