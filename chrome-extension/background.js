/**
 * Pajakia Coretax Co-Pilot — background service worker.
 *
 * Responsibilities:
 * - Periodically check Coretax health via Pajakia API
 * - Auto-save drafts every 30 seconds
 * - Forward messages between content script and Pajakia backend
 * - Show notifications when Coretax is back up after maintenance
 */

const PAJAKIA_API = "https://pajakai.vercel.app/api/v1";
const HEALTH_CHECK_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

// Track Coretax status to alert on transitions
let lastCoretaxStatus = "unknown";

// ──────────────────────────────────────────
// Health Check Loop
// ──────────────────────────────────────────

async function checkCoretaxStatus() {
  try {
    const res = await fetch(`${PAJAKIA_API}/coretax/status`);
    if (!res.ok) return;
    const data = await res.json();

    const newStatus = data.status;
    if (lastCoretaxStatus !== "unknown" && lastCoretaxStatus !== newStatus) {
      // Status changed
      if (newStatus === "operational" && lastCoretaxStatus !== "operational") {
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icons/icon-128.png",
          title: "Coretax sudah UP! 🎉",
          message: "Pajakia akan auto-retry submission Anda yang tertunda.",
          priority: 2,
        });
      } else if (newStatus !== "operational" && lastCoretaxStatus === "operational") {
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icons/icon-128.png",
          title: "Coretax sedang maintenance",
          message: "Pajakia simpan submission di queue. Auto-retry begitu UP.",
          priority: 1,
        });
      }
    }

    lastCoretaxStatus = newStatus;
    chrome.storage.local.set({ coretaxStatus: newStatus, lastChecked: Date.now() });
  } catch (e) {
    console.error("[Pajakia] Health check failed:", e);
  }
}

// Run health check on startup and every 5 min
checkCoretaxStatus();
setInterval(checkCoretaxStatus, HEALTH_CHECK_INTERVAL_MS);

// ──────────────────────────────────────────
// Message Router (content script ↔ background ↔ Pajakia API)
// ──────────────────────────────────────────

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "DECODE_ERROR") {
    decodeError(message.errorMessage).then(sendResponse);
    return true; // async response
  }

  if (message.type === "SAVE_DRAFT") {
    saveDraft(message.draft).then(sendResponse);
    return true;
  }

  if (message.type === "GET_DRAFTS") {
    getDrafts().then(sendResponse);
    return true;
  }

  if (message.type === "QUEUE_SUBMISSION") {
    queueSubmission(message.submission).then(sendResponse);
    return true;
  }

  if (message.type === "VALIDATE_XML") {
    validateXML(message.xml, message.docType).then(sendResponse);
    return true;
  }

  if (message.type === "LOG_AUDIT") {
    logAudit(message.action, message.detail).then(sendResponse);
    return true;
  }
});

async function decodeError(errorMessage) {
  try {
    const token = await getAuthToken();
    const res = await fetch(`${PAJAKIA_API}/coretax/decode-error`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ error_message: errorMessage }),
    });
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    return await res.json();
  } catch (e) {
    return {
      matched: false,
      title: "Tidak dapat decode (offline atau belum login)",
      explanation: e.message,
      fix: "Cek koneksi atau login ke Pajakia.",
    };
  }
}

async function validateXML(xml, docType) {
  try {
    const token = await getAuthToken();
    const res = await fetch(`${PAJAKIA_API}/coretax/validate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ xml_content: xml, type: docType }),
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function queueSubmission(submission) {
  try {
    const token = await getAuthToken();
    const res = await fetch(`${PAJAKIA_API}/coretax/queue`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(submission),
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

// ──────────────────────────────────────────
// Local Draft Storage
// ──────────────────────────────────────────

async function saveDraft(draft) {
  const drafts = await getDrafts();
  const existing = drafts.findIndex((d) => d.url === draft.url);
  const updated = { ...draft, savedAt: Date.now() };

  if (existing >= 0) {
    drafts[existing] = updated;
  } else {
    drafts.push(updated);
  }

  // Keep only last 50 drafts
  const trimmed = drafts.slice(-50);
  await chrome.storage.local.set({ drafts: trimmed });
  return { saved: true, total: trimmed.length };
}

async function getDrafts() {
  const result = await chrome.storage.local.get("drafts");
  return result.drafts || [];
}

// ──────────────────────────────────────────
// Audit Log (local + remote)
// ──────────────────────────────────────────

async function logAudit(action, detail) {
  const result = await chrome.storage.local.get("auditLog");
  const log = result.auditLog || [];
  log.push({
    action,
    detail,
    timestamp: Date.now(),
    url: detail?.url || null,
  });
  // Keep last 500
  await chrome.storage.local.set({ auditLog: log.slice(-500) });
  return { logged: true };
}

// ──────────────────────────────────────────
// Auth helper
// ──────────────────────────────────────────

async function getAuthToken() {
  const result = await chrome.storage.local.get("pajakiaToken");
  return result.pajakiaToken || null;
}
