import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "GTM Copilot",
  description: "Google Tag Manager Copilot GUI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-6">
          <h1 className="text-xl font-bold">GTM Copilot</h1>
          <nav className="flex gap-4 text-sm">
            <Link href="/" className="text-gray-600 hover:text-gray-900">Workspace</Link>
            <Link href="/generate" className="text-gray-600 hover:text-gray-900">AI生成</Link>
            <Link href="/templates" className="text-gray-600 hover:text-gray-900">テンプレート</Link>
            <Link href="/history" className="text-gray-600 hover:text-gray-900">履歴</Link>
          </nav>
        </header>
        <AuthProvider>
          <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
