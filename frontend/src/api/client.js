export const API_DEFAULT = import.meta.env.VITE_AQTIFY_API_BASE || "http://127.0.0.1:8000";

export async function healthCheck(apiBase) {
  const res = await fetch(`${apiBase}/`);
  if (!res.ok) throw new Error("API offline");
  return res.json();
}

export async function createApiKey(apiBase, { userName, userEmail, keyMode = "server" } = {}) {
  const form = new FormData();
  if (userName) form.append("user_name", userName);
  if (userEmail) form.append("user_email", userEmail);
  form.append("key_mode", keyMode);
  const res = await fetch(`${apiBase}/api/keys`, { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Could not create API key.");
  return data;
}

function authHeaders(apiKey) {
  return apiKey ? { "X-API-Key": apiKey } : {};
}

export async function registerMedia(apiBase, apiKey, { file, ownerName, ownerEmail }) {
  const form = new FormData();
  form.append("file", file);
  if (ownerName) form.append("owner_name", ownerName);
  if (ownerEmail) form.append("owner_email", ownerEmail);

  const res = await fetch(`${apiBase}/api/register`, {
    method: "POST",
    body: form,
    headers: authHeaders(apiKey),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Registration failed.");
  return data;
}

export async function downloadSecured(apiBase, apiKey, certificateId) {
  const res = await fetch(`${apiBase}/api/secured/${certificateId}`, {
    headers: authHeaders(apiKey),
  });
  if (!res.ok) throw new Error("Could not download secured file.");
  return res.blob();
}

export async function verifyMedia(apiBase, apiKey, { file, certificateId }) {
  const form = new FormData();
  form.append("file", file);
  if (certificateId) form.append("certificate_id", certificateId);

  const res = await fetch(`${apiBase}/api/verify`, {
    method: "POST",
    body: form,
    headers: authHeaders(apiKey),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Verification failed.");
  if (data.status === "not_found") {
    throw new Error("No authenticity record found for this file — was it registered?");
  }
  return data;
}

export async function fetchManifest(apiBase, apiKey, certificateId) {
  const res = await fetch(`${apiBase}/api/manifest/${certificateId}`, {
    headers: authHeaders(apiKey),
  });
  return res.json();
}

export async function fetchCustodyLog(apiBase, apiKey, certificateId) {
  const res = await fetch(`${apiBase}/api/custody/${certificateId}`, {
    headers: authHeaders(apiKey),
  });
  return res.json();
}

export async function fetchMyRegistrations(apiBase, apiKey) {
  const res = await fetch(`${apiBase}/api/my-registrations`, {
    headers: authHeaders(apiKey),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Could not load registrations.");
  return data;
}

export async function publicVerify(apiBase, { certificateId, hash }) {
  const params = new URLSearchParams();
  if (certificateId) params.set("certificate_id", certificateId);
  if (hash) params.set("hash", hash);
  const res = await fetch(`${apiBase}/api/public-verify?${params}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Not found.");
  return data;
}

export async function registerBulk(apiBase, apiKey, { files, ownerName, ownerEmail }) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  if (ownerName) form.append("owner_name", ownerName);
  if (ownerEmail) form.append("owner_email", ownerEmail);

  const res = await fetch(`${apiBase}/api/register/bulk`, {
    method: "POST",
    body: form,
    headers: authHeaders(apiKey),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Bulk registration failed.");
  return data;
}

export function badgeUrl(apiBase, certificateId) {
  return `${apiBase}/api/badge/${certificateId}.svg`;
}
