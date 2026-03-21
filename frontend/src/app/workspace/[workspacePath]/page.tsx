"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { ExportResponse } from "@/lib/types";

export default function WorkspaceOverview() {
  const params = useParams();
  const workspacePath = decodeURIComponent(params.workspacePath as string);
  const [data, setData] = useState<ExportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .exportWorkspace(workspacePath)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [workspacePath]);

  if (loading) return <div className="text-gray-500">Loading workspace...</div>;
  if (error) return <div className="text-red-600">Error: {error}</div>;
  if (!data) return null;

  const encodedPath = encodeURIComponent(workspacePath);

  const stats = [
    { label: "Tags", count: data.tags.length },
    { label: "Triggers", count: data.triggers.length },
    { label: "Variables", count: data.variables.length },
    { label: "Built-in Variables", count: data.built_in_variables.length },
  ];

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-2">Workspace Overview</h2>
      <p className="text-sm text-gray-500 mb-6 font-mono">{workspacePath}</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-3xl font-bold">{s.count}</div>
            <div className="text-sm text-gray-500">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-4">
        <Link
          href={`/workspace/${encodedPath}/export`}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Export
        </Link>
        <Link
          href={`/workspace/${encodedPath}/import`}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Import
        </Link>
        <Link
          href={`/generate?workspace=${encodedPath}`}
          className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
        >
          AI生成
        </Link>
      </div>
    </div>
  );
}
