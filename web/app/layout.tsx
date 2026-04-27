import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pajakia — Coretax Co-Pilot untuk Konsultan Pajak",
  description:
    "Generator XML, validator pra-upload, dan error decoder Coretax untuk konsultan pajak Indonesia.",
  icons: {
    icon: "/favicon.svg",
  },
  openGraph: {
    title: "Pajakia — Coretax Co-Pilot untuk Konsultan Pajak",
    description: "Generator XML, validator pra-upload, dan error decoder Coretax untuk konsultan pajak Indonesia.",
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
