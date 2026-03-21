"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { SyncStatus } from "@/components/sync/SyncStatus";

export default function ImportPage() {
  const params = useParams();
  const workspacePath = decodeURIComponent(params.workspacePath as string);
  const [importData, setImportData] = useState<ImportData | null>(null);
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [executeResult, setExecuteResult] = useState<ImportExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target?.result as string);
        setImportData(parsed);
        setPreview(null);
        setExecuteResult(null);
        setError("");
      } catch {
        setError("Invalid JSON file");
      }
    };
    reader.readAsText(file);
  };

  const handlePreview = async () => {
    if (!importData) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.importPreview(workspacePath, importData);
      setPreview(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Preview failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!importData) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.importExecute(workspacePath, importData);
      setExecuteResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">Import</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload JSON file
        </label>
        <input
          type="file"
          accept=".json"
          onChange={handleFileUpload}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>

      {importData && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md text-sm">
          Loaded: {importData.tags?.length || 0} tags, {importData.triggers?.length || 0} triggers,{" "}
          {importData.variables?.length || 0} variables, {importData.built_in_variables?.length || 0} built-in variables
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="flex gap-3 mb-6">
        <button
          onClick={handlePreview}
          disabled={!importData || loading}
          className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && !executeResult ? "Loading..." : "Preview Changes"}
        </button>
        <button
          onClick={handleExecute}
          disabled={!importData || loading}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && executeResult ? "Executing..." : "Execute Import"}
        </button>
      </div>

      {preview && !executeResult && <SyncStatus preview={preview} />}
      {executeResult && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Import Results</h3>
          <div className="flex gap-4 mb-4">
            {Object.entries(executeResult.summary).map(([key, val]) => (
              <span key={key} className="text-sm">
                <span className="font-medium">{key}:</span> {val}
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
                  <th className="text-left px-4 py-2">Error</th>
                </tr>
              </thead>
              <tbody>
                {executeResult.results.map((r, i) => (
                  <tr key={i} className="border-t border-gray-100">
                    <td className="px-4 py-2">{r.type}</td>
                    <td className="px-4 py-2 font-mono">{r.name}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                          r.action === "created"
                            ? "bg-green-100 text-green-800"
                            : r.action === "updated"
                            ? "bg-blue-100 text-blue-800"
                            : r.action === "error"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {r.action}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-red-600">{r.error || ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
