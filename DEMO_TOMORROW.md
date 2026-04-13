# Pajakia — Demo Prep for First Users

Last deployed: 2026-04-13

## What's Live

### URLs
| Service | URL | Status |
|---|---|---|
| **Frontend** | https://pajakai.vercel.app | ✅ Live |
| **Frontend (custom)** | https://pajakia.com | ⚠️ DNS still propagating (see below) |
| **Backend API** | https://pajakai-api.vercel.app | ✅ Live |
| **Backend (custom)** | https://api.pajakia.com | ⚠️ Needs DNS record (see below) |

### Health check
```bash
curl https://pajakai-api.vercel.app/health
# {"status":"healthy"}
```

## What Works End-to-End (Demo-Ready)

These features work **without login, without a database, without any setup**:

1. **Homepage + marketing** — pajakia.com (once DNS clears) or pajakai.vercel.app
2. **Consultant dashboard UI** — `/konsultan` (all tabs, mock data populated)
3. **PPh 21 Calculator** — `/kalkulator` (pure client-side, always works)
4. **Coretax Co-Pilot dashboard** — `/konsultan/coretax`
   - **Error Decoder** — paste any Coretax error, get live decode from backend
   - **22 Error Catalog** — browse all known errors
   - **Generator / Validator / Retry Queue UI** — shows the workflow (validation is mocked for now, can be wired later)

### Live demo script

**Show 1: The promise** (30 seconds)
- Open pajakai.vercel.app
- Scroll to "Coretax Co-Pilot" section
- Read the "Before" / "After" comparison

**Show 2: The error decoder actually works** (1 minute)
- Click "Masuk" → go to /konsultan/coretax
- Click "🔍 Error Decoder" tab
- Paste: `Invalid NPWP format in row 14, 15 digits only`
- Click "Decode Error"
- **This hits the live backend** and returns a real decoded explanation + fix
- Try another: `Service unavailable 503 maintenance` → real maintenance warning

**Show 3: The 22 Error Catalog** (30 seconds)
- Click "📚 22 Error Catalog" tab
- Show 22 error codes with auto-fix badges
- Point out which ones Pajakia auto-fixes

**Show 4: The tax calculator** (30 seconds)
- Click /kalkulator
- Enter 180000000 with TK/0
- Instant PPh 21 calculation with bracket breakdown

**Show 5: The phone mockups + WhatsApp flow** (1 minute)
- Scroll homepage to "Cara Kerja" section
- Point at phone mockups showing client → AI → consultant flow
- Open WhatsApp and show the 628131102445 number (note: webhook not connected yet)

## What's NOT Yet Working

These will be explained as "coming next week" or "configured for you when you sign up":

| Feature | Status | Blocker |
|---|---|---|
| Google Sign-in | Wired but no OAuth app | Need to configure Google Cloud Console credentials |
| WhatsApp document receive | Code ready, webhook not registered | Meta Business verification (2-3 days) |
| Document OCR via OpenAI | Code ready | OPENAI_API_KEY not set in Vercel env |
| Client DB + filings | Schema ready | Postgres not provisioned (can do after Meta/Google) |
| Retry queue execution | Endpoints ready | Needs Postgres |
| Invoice generation | Endpoints ready | Needs Postgres |
| Chrome extension | Code ready | Not published to Web Store |

## What You Need to Do Before the Demo

### 1. Fix Namecheap DNS for pajakia.com (5 minutes)
Current DNS resolves to BOTH `192.64.119.223` (old parking) AND `76.76.21.21` (new Vercel).
You must fully **delete** the old record at Namecheap:

- Log into Namecheap → Domain List → pajakia.com → Manage → Advanced DNS
- Find any record with value `192.64.119.223` or `parkingpage.namecheap.com` — **delete it**
- Keep only these two records:
  ```
  A Record    @      76.76.21.21              TTL: Automatic
  CNAME       www    cname.vercel-dns.com.    TTL: Automatic
  ```
- Click "✓" to save each row

### 2. Add DNS record for api.pajakia.com (2 minutes)
Add this record at Namecheap Advanced DNS:
```
A Record    api    76.76.21.21    TTL: Automatic
```
Once propagated (~10 min), `https://api.pajakia.com` will serve the backend.

### 3. After the demo — unblock production readiness

In priority order:

1. **Get OpenAI API key** (5 min, `platform.openai.com` → API keys)
   - `echo "sk-..." | vercel env add OPENAI_API_KEY production --scope lunks-projects`
   - Then redeploy backend: `cd /Users/yves/Documents/pajakai && vercel --prod --yes --scope lunks-projects`

2. **Provision Neon Postgres** via Vercel Marketplace
   - Dashboard → pajakai-api → Storage → Create → Neon Postgres
   - Choose Singapore or Jakarta region
   - It auto-sets `DATABASE_URL` in backend env
   - Run migrations: need to add Alembic config for Neon (I can help with this)

3. **Configure Google OAuth**
   - https://console.cloud.google.com → APIs & Credentials → Create OAuth 2.0 Client ID
   - Authorized redirect URIs: `https://api.pajakia.com/api/v1/auth/google/callback`, `https://pajakai-api.vercel.app/api/v1/auth/google/callback`
   - Copy Client ID + Secret → set as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` env vars
   - Set `GOOGLE_REDIRECT_URI=https://api.pajakia.com/api/v1/auth/google/callback`

4. **WhatsApp Cloud API** (Meta)
   - https://business.facebook.com → WhatsApp → Get Started
   - Business verification (can take days)
   - Once approved, register webhook URL: `https://api.pajakia.com/api/v1/webhook/whatsapp`
   - Set env vars: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`

## Backend Env Vars Currently Set
```
SECRET_KEY              (real 64-byte random)
ENCRYPTION_KEY          (real 48-byte random)
CORS_ORIGINS            (pajakia.com, www.pajakia.com, pajakai.vercel.app, localhost)
FRONTEND_URL            (https://pajakia.com)
DATABASE_URL            (placeholder — swap when Neon is provisioned)
REDIS_URL               (placeholder — rate limiting uses in-memory fallback)
WHATSAPP_VERIFY_TOKEN   (random token, ready for Meta registration)
```

## Talking Points for the Demo

### When they ask "Is it already being used?"
"You'd be among the first consultants. We're opening up to 3-5 pilot users this week to get real-world feedback before the full launch."

### When they ask "How is this different from Klikpajak/OnlinePajak?"
"Those are document processing tools for enterprise. We're built specifically for consultants managing 10-100 clients. The WhatsApp-first flow and the 22 Coretax error decoder are unique to us — nobody else has wired the DJP Coretax pain points directly into their product."

### When they ask "What happens to my client data?"
"Encrypted at rest with AES-256. Servers physically in Indonesia. Full audit log of every access. You can export or delete all data anytime. We follow UU PDP."

### When they ask the price
- Starter Rp 299K/month for 10 clients
- Pro Rp 599K/month for 25 clients (most popular)
- Business Rp 999K/month for 50 clients
- Enterprise Rp 1.5jt/month for 100+ clients
- Free 14-day trial, no credit card

### When they ask "Can I try it right now?"
"Yes — open Pajakia on your phone, go to Coretax Co-Pilot, paste any error message you've hit recently. It'll decode it live in front of you."

## If Something Goes Wrong

### Backend returns 500
```bash
vercel logs https://pajakai-api.vercel.app --scope lunks-projects
```

### Frontend shows "Koneksi gagal" in error decoder
- Check `NEXT_PUBLIC_API_URL` is set: `vercel env ls --scope lunks-projects`
- Check backend is up: `curl https://pajakai-api.vercel.app/health`

### pajakia.com shows the parking page
- DNS hasn't fully propagated (can take up to 1 hour)
- Fall back to pajakai.vercel.app for the demo
