# Pajakia Pilot Demo Plan

## Demo Positioning

Lead with a narrow, credible wedge:

> Pajakia is a Coretax Co-Pilot for Indonesian tax consultants. It helps generate XML, catch common Coretax errors before upload, and explain rejection messages in plain Indonesian.

Do not lead with full WhatsApp OCR automation yet. Treat WhatsApp document intake as the next pilot workflow after the consultant validates the Coretax pain point.

## 20-Minute Consultant Demo

1. **Problem framing (2 min)**
   - Ask: "What Coretax errors or upload failures cost you the most time this month?"
   - Ask: "How many clients do you manage during masa/tahunan deadline weeks?"

2. **Coretax Error Decoder (5 min)**
   - Open `/konsultan/coretax`.
   - Click sample: `Invalid NPWP format in row 14, 15 digits only`.
   - Paste one real error message from the consultant if they have one.
   - Outcome to watch: do they say "yes, this happens" or ask to try another error?

3. **XML Generator (5 min)**
   - Click "Isi contoh generator".
   - Show required columns and template download.
   - Generate XML from sample data.
   - Outcome to watch: do they already have Excel templates this could adapt to?

4. **Validator Pra-Upload (3 min)**
   - Explain that the goal is fewer rejected uploads, not replacing the consultant.
   - Show 22 Error Catalog.

5. **Dashboard / Business Ops (3 min)**
   - Open `/konsultan`.
   - Show deadline board, client list, invoices, activity log.
   - Say explicitly: "This dashboard data is demo data; the Coretax tools are the live part."

6. **Close for pilot (2 min)**
   - Ask for 3 anonymized Excel/XML examples or 3 real Coretax error messages.
   - Offer a 14-day pilot.

## Pilot Offer

- Starter pilot: Rp 299rb/month after 14-day trial
- Best first ask: "Send me 3 real Coretax errors and 1 anonymized Excel template."
- Success criterion: save at least 2 hours/week or prevent 3+ rejected uploads in the first month.

## What Must Be True Before This Is A Real Business

1. **One painful job-to-be-done is validated**
   - At least 5 consultants confirm Coretax error decoding / XML validation is painful enough to pay for.
   - At least 2 consultants provide real sample files or error messages.

2. **Coretax tools work reliably**
   - Generator handles their actual Excel columns or has a mapping step.
   - Validator catches the top recurring errors.
   - Decoder has useful fixes for real messages, not only synthetic examples.

3. **Trust is explicit**
   - Demo states what is live vs sample data.
   - Security claims map to real implementation: encrypted storage, access logs, deletion/export path.

4. **Pilot onboarding is manual but tight**
   - WhatsApp or Google login can be configured later.
   - For the first 3-5 consultants, manually onboard them and adapt templates.

5. **Payment path is simple**
   - Start with transfer + WhatsApp proof.
   - Invoice monthly after the trial.
   - Do not build complex billing before the pilot converts.

## Red Flags To Listen For

- "We do not use Excel before Coretax" -> reposition around error decoder only.
- "My staff already knows how to fix these" -> ask whether junior staff or peak season still creates bottlenecks.
- "Data privacy is the blocker" -> offer anonymized/offline Excel validation first.
- "I need WhatsApp intake first" -> treat as custom pilot, not generic launch.
