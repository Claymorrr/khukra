import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Khukra Logistics",
  description: "Global disruption forecast and statistical risk discovery",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#080a0e] text-zinc-100 antialiased">{children}</body>
    </html>
  );
}
