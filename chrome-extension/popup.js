/**
 * Pajakia Coretax Co-Pilot — popup script.
 * Shows quick stats and actions when user clicks the extension icon.
 */

(async function () {
  const statusEl = document.getElementById("status");
  const statusText = document.getElementById("status-text");
  const draftCount = document.getElementById("draft-count");
  const decodedCount = document.getElementById("decoded-count");

  // Fetch Coretax status from local storage (set by background.js)
  const stored = await chrome.storage.local.get(["coretaxStatus", "lastChecked", "drafts", "auditLog"]);

  const status = stored.coretaxStatus || "unknown";
  if (status === "operational") {
    statusEl.className = "status status-ok";
    statusText.textContent = "Coretax: Operational ✓";
  } else if (status === "maintenance") {
    statusEl.className = "status status-warn";
    statusText.textContent = "Coretax: Maintenance";
  } else if (status === "down") {
    statusEl.className = "status status-down";
    statusText.textContent = "Coretax: Down ✗";
  } else {
    statusEl.className = "status status-warn";
    statusText.textContent = "Coretax: Memeriksa...";
  }

  // Stats
  draftCount.textContent = (stored.drafts || []).length;
  const decoded = (stored.auditLog || []).filter((a) => a.action === "decoded_error").length;
  decodedCount.textContent = decoded;

  // Action buttons
  document.getElementById("open-coretax").addEventListener("click", () => {
    chrome.tabs.create({ url: "https://coretax.pajak.go.id/" });
  });

  document.getElementById("view-drafts").addEventListener("click", async () => {
    const drafts = stored.drafts || [];
    if (drafts.length === 0) {
      alert("Belum ada draft tersimpan.");
      return;
    }
    const list = drafts
      .slice(-10)
      .reverse()
      .map((d, i) => `${i + 1}. ${d.title || "Untitled"} (${new Date(d.savedAt || d.timestamp).toLocaleString("id-ID")})`)
      .join("\n");
    alert(`10 Draft Terbaru:\n\n${list}`);
  });

  document.getElementById("view-audit").addEventListener("click", () => {
    const log = stored.auditLog || [];
    if (log.length === 0) {
      alert("Belum ada audit log.");
      return;
    }
    const list = log
      .slice(-10)
      .reverse()
      .map((a) => `[${new Date(a.timestamp).toLocaleString("id-ID")}] ${a.action}`)
      .join("\n");
    alert(`10 Audit Terbaru:\n\n${list}`);
  });
})();
