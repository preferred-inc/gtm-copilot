import type { Metadata } from "next";
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
            <a href="/" className="text-gray-600 hover:text-gray-900">Workspace</a>
            <a href="/generate" className="text-gray-600 hover:text-gray-900">AI生成</a>
            <a href="/templates" className="text-gray-600 hover:text-gray-900">テンプレート</a>
            <a href="/history" className="text-gray-600 hover:text-gray-900">履歴</a>
          </nav>
        </header>
        <AuthProvider>
          <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
