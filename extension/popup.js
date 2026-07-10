const apiBaseInput = document.getElementById("apiBase");
const apiKeyInput = document.getElementById("apiKey");
const status = document.getElementById("status");

chrome.storage.local.get(["apiBase", "apiKey"], (stored) => {
  apiBaseInput.value = stored.apiBase || "http://127.0.0.1:8000";
  apiKeyInput.value = stored.apiKey || "";
});

document.getElementById("save").addEventListener("click", () => {
  chrome.storage.local.set(
    { apiBase: apiBaseInput.value.trim(), apiKey: apiKeyInput.value.trim() },
    () => {
      status.style.display = "block";
      setTimeout(() => (status.style.display = "none"), 1500);
    }
  );
});
