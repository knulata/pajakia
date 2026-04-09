/**
 * Pajakia Coretax Co-Pilot — content script.
 *
 * Injects into coretax.pajak.go.id pages to:
 * - Detect error messages on the page → decode them inline
 * - Auto-save form drafts every 30 seconds
 * - Show floating action button (FAB) for quick actions
 * - Sanitize NPWP/NIK fields as user types
 */

(function () {
  "use strict";

  const PJK_PREFIX = "[Pajakia]";
  const SAVE_INTERVAL_MS = 30 * 1000; // 30 seconds

  // ──────────────────────────────────────────
  // Floating Action Button (FAB)
  // ──────────────────────────────────────────

  function injectFAB() {
    if (document.getElementById("pjk-fab")) return;

    const fab = document.createElement("div");
    fab.id = "pjk-fab";
    fab.innerHTML = `
      <div class="pjk-fab-button" title="Pajakia Co-Pilot">
        <span class="pjk-fab-icon">⚡</span>
      </div>
      <div class="pjk-fab-menu" style="display:none">
        <button class="pjk-fab-action" data-action="save-draft">💾 Save Draft</button>
        <button class="pjk-fab-action" data-action="view-drafts">📋 View Drafts</button>
        <button class="pjk-fab-action" data-action="decode-error">🔍 Decode Last Error</button>
        <button class="pjk-fab-action" data-action="open-pajakia">🚀 Open Pajakia</button>
      </div>
    `;
    document.body.appendChild(fab);

    const button = fab.querySelector(".pjk-fab-button");
    const menu = fab.querySelector(".pjk-fab-menu");
    button.addEventListener("click", () => {
      menu.style.display = menu.style.display === "none" ? "flex" : "none";
    });

    fab.querySelectorAll(".pjk-fab-action").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.dataset.action;
        menu.style.display = "none";
        handleAction(action);
      });
    });
  }

  function handleAction(action) {
    switch (action) {
      case "save-draft":
        saveCurrentDraft(true);
        break;
      case "view-drafts":
        chrome.runtime.sendMessage({ type: "GET_DRAFTS" }, (drafts) => {
          showDraftsModal(drafts || []);
        });
        break;
      case "decode-error":
        decodeLastError();
        break;
      case "open-pajakia":
        window.open("https://pajakai.vercel.app/konsultan/coretax", "_blank");
        break;
    }
  }

  // ──────────────────────────────────────────
  // Error Detection & Inline Decoding
  // ──────────────────────────────────────────

  function detectAndDecodeErrors() {
    // Common Coretax error containers
    const errorSelectors = [
      ".alert-danger",
      ".error-message",
      "[role='alert']",
      ".validation-error",
      ".text-danger",
    ];

    errorSelectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((el) => {
        if (el.dataset.pjkDecoded) return; // already processed
        el.dataset.pjkDecoded = "true";

        const errorText = el.textContent.trim();
        if (!errorText || errorText.length < 5) return;

        // Ask background to decode
        chrome.runtime.sendMessage(
          { type: "DECODE_ERROR", errorMessage: errorText },
          (decoded) => {
            if (decoded && (decoded.matched || decoded.title)) {
              injectDecoderInline(el, decoded);
            }
          }
        );
      });
    });
  }

  function injectDecoderInline(errorElement, decoded) {
    const banner = document.createElement("div");
    banner.className = "pjk-decoder-banner";
    banner.innerHTML = `
      <div class="pjk-decoder-header">
        <span class="pjk-decoder-icon">${decoded.severity === "critical" ? "🚨" : "💡"}</span>
        <strong>Pajakia decode:</strong>
        <span>${escapeHtml(decoded.title || "Solusi tersedia")}</span>
      </div>
      <div class="pjk-decoder-body">
        <div class="pjk-decoder-explanation">${escapeHtml(decoded.explanation || "")}</div>
        <div class="pjk-decoder-fix"><strong>Fix:</strong> ${escapeHtml(decoded.fix || "")}</div>
      </div>
    `;

    errorElement.parentNode.insertBefore(banner, errorElement.nextSibling);
    chrome.runtime.sendMessage({
      type: "LOG_AUDIT",
      action: "decoded_error",
      detail: { errorText: errorElement.textContent.trim().slice(0, 200), url: location.href },
    });
  }

  function decodeLastError() {
    const errors = document.querySelectorAll(".alert-danger, [role='alert'], .text-danger");
    if (errors.length === 0) {
      showToast("Tidak ada error di halaman ini.");
      return;
    }
    const lastError = errors[errors.length - 1];
    const text = lastError.textContent.trim();
    chrome.runtime.sendMessage(
      { type: "DECODE_ERROR", errorMessage: text },
      (decoded) => {
        if (decoded) {
          alert(
            `${decoded.title}\n\n${decoded.explanation || ""}\n\nFIX:\n${decoded.fix || ""}`
          );
        }
      }
    );
  }

  // ──────────────────────────────────────────
  // Auto-Save Drafts
  // ──────────────────────────────────────────

  function saveCurrentDraft(showFeedback = false) {
    // Capture all form field values on the current page
    const formData = {};
    document.querySelectorAll("input, select, textarea").forEach((field) => {
      if (!field.name && !field.id) return;
      const key = field.name || field.id;
      if (field.type === "password" || field.type === "hidden") return; // never save these
      formData[key] = field.value;
    });

    if (Object.keys(formData).length === 0) return;

    const draft = {
      url: location.href,
      title: document.title,
      formData,
      timestamp: Date.now(),
    };

    chrome.runtime.sendMessage({ type: "SAVE_DRAFT", draft }, (resp) => {
      if (showFeedback && resp?.saved) {
        showToast(`Draft saved (${Object.keys(formData).length} fields)`);
      }
    });
  }

  // ──────────────────────────────────────────
  // NPWP/NIK Sanitization
  // ──────────────────────────────────────────

  function sanitizeFields() {
    const npwpSelectors = "input[name*='npwp' i], input[id*='npwp' i], input[placeholder*='NPWP' i]";
    document.querySelectorAll(npwpSelectors).forEach((field) => {
      if (field.dataset.pjkWatched) return;
      field.dataset.pjkWatched = "true";

      field.addEventListener("blur", () => {
        const original = field.value;
        const sanitized = sanitizeNPWP(original);
        if (original !== sanitized && sanitized) {
          field.value = sanitized;
          field.style.background = "#dcfce7";
          showToast(`NPWP auto-fixed: ${original} → ${sanitized}`);
          setTimeout(() => (field.style.background = ""), 2000);
        }
      });
    });
  }

  function sanitizeNPWP(value) {
    if (!value) return "";
    let s = String(value).trim();
    if (/^\d+\.?\d*[Ee][+-]?\d+$/.test(s)) {
      try {
        s = String(parseInt(parseFloat(s), 10));
      } catch (e) {}
    }
    const digits = s.replace(/\D/g, "");
    if (!digits) return "";
    if (digits.length === 15) return "0" + digits;
    if (digits.length < 16) return digits.padStart(16, "0");
    return digits.slice(0, 16);
  }

  // ──────────────────────────────────────────
  // Drafts Modal
  // ──────────────────────────────────────────

  function showDraftsModal(drafts) {
    const existing = document.getElementById("pjk-drafts-modal");
    if (existing) existing.remove();

    const modal = document.createElement("div");
    modal.id = "pjk-drafts-modal";
    modal.innerHTML = `
      <div class="pjk-modal-backdrop"></div>
      <div class="pjk-modal-content">
        <div class="pjk-modal-header">
          <h3>Saved Drafts (${drafts.length})</h3>
          <button class="pjk-modal-close">×</button>
        </div>
        <div class="pjk-modal-body">
          ${drafts.length === 0 ? '<p>No drafts saved yet.</p>' : drafts.reverse().map((d, i) => `
            <div class="pjk-draft-item" data-index="${i}">
              <div class="pjk-draft-title">${escapeHtml(d.title || 'Untitled')}</div>
              <div class="pjk-draft-meta">${new Date(d.savedAt || d.timestamp).toLocaleString('id-ID')} — ${Object.keys(d.formData || {}).length} fields</div>
              <div class="pjk-draft-url">${escapeHtml(d.url)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector(".pjk-modal-close").addEventListener("click", () => modal.remove());
    modal.querySelector(".pjk-modal-backdrop").addEventListener("click", () => modal.remove());
  }

  // ──────────────────────────────────────────
  // Toast notifications
  // ──────────────────────────────────────────

  function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "pjk-toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add("pjk-toast-show"), 10);
    setTimeout(() => {
      toast.classList.remove("pjk-toast-show");
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // ──────────────────────────────────────────
  // Init
  // ──────────────────────────────────────────

  function init() {
    console.log(PJK_PREFIX, "Coretax Co-Pilot active on", location.href);
    injectFAB();
    detectAndDecodeErrors();
    sanitizeFields();

    // Watch for dynamic content (Coretax is SPA-like)
    const observer = new MutationObserver(() => {
      detectAndDecodeErrors();
      sanitizeFields();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Auto-save drafts every 30 seconds
    setInterval(() => saveCurrentDraft(false), SAVE_INTERVAL_MS);

    // Save on navigation away
    window.addEventListener("beforeunload", () => saveCurrentDraft(false));

    // Audit page visit
    chrome.runtime.sendMessage({
      type: "LOG_AUDIT",
      action: "page_view",
      detail: { url: location.href, title: document.title },
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
