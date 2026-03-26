"use client";

import { useState } from "react";

interface ActivityEntry { action: string; resource_type: string; resource_id: string; detail: string | null; ip_address: string | null; timestamp: string; }

const mockActivity: ActivityEntry[] = [
  { action: "view_client", resource_type: "client", resource_id: "c1", detail: "PT Maju Bersama", ip_address: "103.28.12.45", timestamp: "2026-03-26T10:30:00Z" },
  { action: "verify_document", resource_type: "document", resource_id: "d1", detail: "corrections=2", ip_address: "103.28.12.45", timestamp: "2026-03-26T10:25:00Z" },
  { action: "create_invoice", resource_type: "invoice", resource_id: "i5", detail: "INV-202603-0005 for CV Sinar Abadi", ip_address: "103.28.12.45", timestamp: "2026-03-26T09:15:00Z" },
  { action: "request_documents", resource_type: "client", resource_id: "c3", detail: "Requested 3 doc types via WhatsApp", ip_address: "103.28.12.45", timestamp: "2026-03-25T16:00:00Z" },
  { action: "update_filing_status", resource_type: "filing", resource_id: "f7", detail: "review -> approved", ip_address: "103.28.12.45", timestamp: "2026-03-25T15:30:00Z" },
  { action: "export_client_data", resource_type: "client", resource_id: "c2", detail: null, ip_address: "103.28.12.45", timestamp: "2026-03-25T14:00:00Z" },
  { action: "bulk_import_clients", resource_type: "client", resource_id: "", detail: "Imported 15 clients", ip_address: "103.28.12.45", timestamp: "2026-03-24T11:00:00Z" },
];

function actionLabel(a: string) {
  const labels: Record<string, string> = { view_client: "Lihat Klien", create_client: "Buat Klien", update_client: "Update Klien", verify_document: "Verifikasi Dokumen", create_invoice: "Buat Invoice", request_documents: "Request Dokumen", update_filing_status: "Update Status Filing", export_client_data: "Export Data Klien", bulk_import_clients: "Import Bulk Klien", portal_upload: "Upload Portal", grant_consent: "Persetujuan Diberikan", revoke_consent: "Persetujuan Dicabut" };
  return labels[a] || a;
}

function actionIcon(a: string) {
  if (a.includes("create") || a.includes("import")) return "➕";
  if (a.includes("view")) return "👁";
  if (a.includes("verify")) return "✅";
  if (a.includes("invoice")) return "💰";
  if (a.includes("request")) return "💬";
  if (a.includes("update")) return "✏️";
  if (a.includes("export")) return "📦";
  if (a.includes("delete")) return "🗑";
  return "📝";
}

export default function ActivityLogPage() {
  const [filterAction, setFilterAction] = useState("");
  const filtered = filterAction ? mockActivity.filter((a) => a.action === filterAction) : mockActivity;
  const uniqueActions = [...new Set(mockActivity.map((a) => a.action))];

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-extrabold">Log Aktivitas</h1><p className="text-sm text-[var(--text-secondary)]">Semua akses dan perubahan data tercatat untuk transparansi</p></div>
      <div className="flex gap-2 flex-wrap">
        <button onClick={() => setFilterAction("")} className={`rounded-lg px-3 py-1.5 text-sm font-medium ${!filterAction ? "bg-[var(--primary)] text-white" : "border border-[var(--border)] hover:bg-gray-50"}`}>Semua</button>
        {uniqueActions.map((a) => (<button key={a} onClick={() => setFilterAction(a)} className={`rounded-lg px-3 py-1.5 text-sm font-medium ${filterAction === a ? "bg-[var(--primary)] text-white" : "border border-[var(--border)] hover:bg-gray-50"}`}>{actionLabel(a)}</button>))}
      </div>
      <div className="rounded-xl border border-[var(--border)] bg-white shadow-sm">
        <div className="divide-y divide-[var(--border)]">
          {filtered.map((entry, i) => (
            <div key={i} className="flex items-start gap-4 px-6 py-4 hover:bg-gray-50">
              <span className="mt-0.5 text-lg">{actionIcon(entry.action)}</span>
              <div className="flex-1">
                <div className="font-medium text-sm">{actionLabel(entry.action)}</div>
                {entry.detail && <div className="text-sm text-[var(--text-secondary)]">{entry.detail}</div>}
                <div className="mt-1 flex gap-3 text-xs text-[var(--text-secondary)]">
                  <span>{new Date(entry.timestamp).toLocaleString("id-ID")}</span>
                  {entry.ip_address && <span>IP: {entry.ip_address}</span>}
                  {entry.resource_id && <span className="font-mono">{entry.resource_type}:{entry.resource_id}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-800"><strong>Transparansi:</strong> Setiap kali data klien diakses atau diubah, dicatat secara otomatis. Log ini dapat di-export dan ditunjukkan kepada klien.</div>
    </div>
  );
}
