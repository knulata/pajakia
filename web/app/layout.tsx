import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pajakia — Asisten Pajak Cerdas Indonesia",
  description:
    "Hitung PPh 21, siapkan SPT, scan bukti potong — semua dengan bantuan AI. Gratis untuk individu.",
  openGraph: {
    title: "Pajakia — Asisten Pajak Cerdas Indonesia",
    description: "Hitung pajak, siapkan SPT, scan dokumen. Gratis.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
