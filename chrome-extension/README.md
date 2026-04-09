# Pajakia Coretax Co-Pilot — Chrome Extension

A Chrome extension that sits on top of [coretax.pajak.go.id](https://coretax.pajak.go.id) and helps Indonesian tax consultants survive Coretax's bugs.

## Features

- **Inline error decoder** — detects Coretax error messages on the page and shows plain-language explanations + fixes
- **Auto-save drafts** — captures form state every 30 seconds (Coretax loses your work on timeout)
- **NPWP auto-sanitizer** — fixes Excel scientific notation and 15-digit NPWP on blur
- **Floating action button** — quick access to drafts, error decoder, and Pajakia dashboard
- **Coretax status monitor** — alerts when Coretax goes down or comes back up
- **Audit log** — records every action for compliance

## Install (Developer Mode)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this `chrome-extension/` folder
5. Pin the extension to your toolbar

## How It Works

The extension only activates on `coretax.pajak.go.id`. It uses a content script to:
- Watch for error messages in the DOM
- Send each error to the Pajakia API for decoding
- Inject the decoded explanation inline next to the original error
- Auto-save form fields to local storage every 30 seconds
- Sanitize NPWP/NIK fields on blur

The background service worker:
- Polls the Pajakia API every 5 minutes for Coretax status
- Shows desktop notifications when status changes
- Routes messages between content script and Pajakia backend
- Stores drafts and audit log in `chrome.storage.local`

## Connecting to Pajakia

The extension talks to `https://pajakai.vercel.app/api/v1` for:
- `POST /coretax/decode-error` — decode Coretax error messages
- `POST /coretax/validate` — validate XML before upload
- `POST /coretax/queue` — queue submissions for auto-retry
- `GET /coretax/status` — check Coretax health

To authenticate, the extension reads `pajakiaToken` from `chrome.storage.local`. Set it once after logging in to Pajakia (the web app injects this automatically).

## Development

This is a Manifest V3 extension with no build step — pure JS/CSS. To modify:

```
chrome-extension/
├── manifest.json    # Extension manifest (MV3)
├── background.js    # Service worker (health checks, API proxy, storage)
├── content.js       # Injected into Coretax pages (error decoder, FAB, sanitizer)
├── overlay.css      # UI styles for injected elements
├── popup.html       # Toolbar popup
├── popup.js         # Popup logic
└── icons/           # Extension icons (16, 48, 128)
```

After editing, click the reload icon on the extension card in `chrome://extensions/`.

## Privacy

- The extension only sends error messages and form metadata to the Pajakia API
- It never sends NPWP, NIK, or financial values to any third party
- Drafts are stored locally in `chrome.storage.local` (your machine only)
- Audit log is local-first; can be synced to Pajakia for compliance reporting

## License

Internal — part of the Pajakia platform.
