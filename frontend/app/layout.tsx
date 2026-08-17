import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Product Intelligence AI | B2B Industrial Catalog Platform",
  description: "Evidence-driven product data enrichment, validation, confidence scoring, and review platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 min-h-screen antialiased selection:bg-indigo-500 selection:text-white`}>
        {children}
      </body>
    </html>
  );
}
