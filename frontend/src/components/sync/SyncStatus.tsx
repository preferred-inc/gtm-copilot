"use client";

import type { ImportPreviewResponse } from "@/lib/types";

export function SyncStatus({ preview }: { preview: ImportPreviewResponse }) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">Preview</h3>
      <div className="flex gap-4 mb-4">
        {Object.entries(preview.summary).map(([key, val]) => (
          <span key={key} className="text-sm">
            <span className="font-medium capitalize">{key}:</span> {val}
          </span>
        ))}
      </div>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left px-4 py-2">Type</th>
              <th className="text-left px-4 py-2">Name</th>
              <th className="text-left px-4 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {preview.diffs.map((d, i) => (
              <tr key={i} className="border-t border-gray-100">
                <td className="px-4 py-2">{d.type}</td>
                <td className="px-4 py-2 font-mono">{d.name}</td>
                <td className="px-4 py-2">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                      d.action === "create"
                        ? "bg-green-100 text-green-800"
                        : d.action === "update"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {d.action}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
