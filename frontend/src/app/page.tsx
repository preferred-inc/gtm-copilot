"use client";

import { useAuth } from "@/lib/auth";
import { WorkspaceConnect } from "@/components/workspace/WorkspaceConnect";

export default function Home() {
  const { isLoggedIn, loading, login, logout } = useAuth();

  if (loading) {
    return <div className="text-gray-500">Loading...</div>;
  }

  if (!isLoggedIn) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h2 className="text-2xl font-semibold mb-4">GTM Copilot</h2>
        <p className="text-gray-500 mb-8">
          Sign in with your Google account to manage GTM workspaces.
        </p>
        <button
          onClick={login}
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
        >
          Sign in with Google
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Connect to GTM Workspace</h2>
        <button
          onClick={logout}
          className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-100"
        >
          Logout
        </button>
      </div>
      <WorkspaceConnect />
    </div>
  );
}
