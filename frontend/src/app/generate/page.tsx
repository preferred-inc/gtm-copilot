"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api, APIError } from "@/lib/api";
import type {
  GenerateResponse,
  ImportData,
  ImportExecuteResponse,
} from "@/lib/types";
import { AnalysisResult } from "@/components/generate/AnalysisResult";
import { ConfigPreview } from "@/components/generate/ConfigPreview";

export default function GeneratePage() {
  return (
    <Suspense fallback={<div className="text-gray-500">Loading...</div>}>
      <GeneratePageInner />
    </Suspense>
  );
}

function GeneratePageInner() {
  const searchParams = useSearchParams();
  const workspaceFromQuery = searchParams.get("workspace") || "";

  const { isLoggedIn, loading: authLoading } = useAuth();
  const [url, setUrl] = useState("");
  const [workspacePath, setWorkspacePath] = useState(workspaceFromQuery);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0); // 0: idle, 1: crawling, 2: generating
  const [error, setError] = useState("");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [applying, setApplying] = useState(false);
  const [applyResult, setApplyResult] = useState<ImportExecuteResponse | null>(
    null
  );

  const handleGenerate = async () => {
    const trimmed = url.trim();
    if (!trimmed) return;

    // Client-side URL validation
    try {
      const parsed = new URL(trimmed);
      if (!["http:", "https:"].includes(parsed.protocol)) {
        setError("URLはhttp://またはhttps://で始まる必要があります");
        return;
      }
    } catch {
      setError("有効なURLを入力してください");
      return;
    }

    setLoading(true);
    setLoadingStep(1);
    setError("");
    setResult(null);
    setApplyResult(null);

    // Simulate step progression (actual API is single request)
    const stepTimer = setTimeout(() => setLoadingStep(2), 15_000);

    try {
      let res: GenerateResponse;
      if (workspacePath && isLoggedIn) {
        res = await api.generateWithWorkspace(trimmed, workspacePath);
      } else {
        res = await api.generate(trimmed);
      }
      setResult(res);
    } catch (e) {
      if (e instanceof DOMException && e.name === "TimeoutError") {
        setError("タイムアウトしました。しばらく経ってから再度お試しください。");
      } else if (e instanceof APIError && e.status === 429) {
        setError("リクエスト数が上限を超えました。しばらく待ってから再試行してください。");
      } else {
        setError(e instanceof Error ? e.message : "生成に失敗しました");
      }
    } finally {
      clearTimeout(stepTimer);
      setLoading(false);
      setLoadingStep(0);
    }
  };

  const handleApply = async (filteredConfig: ImportData) => {
    let targetPath = workspacePath;
    if (!targetPath) {
      const input = prompt(
        "GTM Workspace Path を入力してください\n(例: accounts/123/containers/456/workspaces/789)"
      );
      if (!input) return;
      targetPath = input;
      setWorkspacePath(input);
    }

    setApplying(true);
    setError("");
    try {
      const res = await api.importExecute(targetPath, filteredConfig);
      setApplyResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "適用に失敗しました");
    } finally {
      setApplying(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result.config, null, 2)], {
      type: "application/json",
    });
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "gtm-config.json";
    a.click();
    URL.revokeObjectURL(downloadUrl);
  };

  if (authLoading) {
    return <div className="text-gray-500">Loading...</div>;
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">GTM設定を自動生成</h2>

      {/* URL Input */}
      <div className="space-y-3 mb-6">
        <div className="flex gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          />
          <button
            onClick={handleGenerate}
            disabled={loading || !url.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? "分析中..." : "生成"}
          </button>
        </div>

        {/* Workspace Path (optional) */}
        {isLoggedIn && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-500 whitespace-nowrap">
              Workspace:
            </label>
            <input
              type="text"
              value={workspacePath}
              onChange={(e) => setWorkspacePath(e.target.value)}
              placeholder="accounts/.../workspaces/... (省略可)"
              className="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        )}
      </div>

      {/* Loading with step indicator */}
      {loading && (
        <div className="bg-white border border-gray-200 rounded-lg p-8 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <div>
              <p className="font-medium text-gray-800">
                {loadingStep <= 1
                  ? "サイトを分析しています..."
                  : "GTM設定を生成しています..."}
              </p>
              <p className="text-sm text-gray-400">
                30秒〜1分ほどかかります
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <StepBadge step={1} current={loadingStep} label="サイト分析" />
            <StepBadge step={2} current={loadingStep} label="AI生成" />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-6">
          <AnalysisResult analysis={result.analysis} />
          <ConfigPreview
            config={result.config}
            explanations={result.explanations}
            onApply={handleApply}
            onDownload={handleDownload}
            applying={applying}
          />
        </div>
      )}

      {/* Apply Result */}
      {applyResult && (
        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-800 mb-3">
            適用完了
          </h3>
          <div className="flex gap-4 text-sm">
            {Object.entries(applyResult.summary).map(([action, count]) => (
              <span key={action} className="text-green-700">
                {action}: {count}
              </span>
            ))}
          </div>
          <div className="mt-3 space-y-1">
            {applyResult.results.map((r, i) => (
              <div key={i} className="text-sm flex gap-2">
                <span
                  className={
                    r.action === "error" ? "text-red-600" : "text-green-600"
                  }
                >
                  [{r.action}]
                </span>
                <span>{r.name}</span>
                {r.error && (
                  <span className="text-red-500 text-xs">({r.error})</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info when not logged in */}
      {!isLoggedIn && (
        <p className="text-sm text-gray-400 mt-4">
          ※
          GTMへの適用にはログインが必要です。生成・プレビューはログインなしで利用できます。
        </p>
      )}
    </div>
  );
}

function StepBadge({
  step,
  current,
  label,
}: {
  step: number;
  current: number;
  label: string;
}) {
  const isDone = current > step;
  const isActive = current === step;

  return (
    <div
      className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
        isDone
          ? "bg-green-100 text-green-700"
          : isActive
            ? "bg-blue-100 text-blue-700"
            : "bg-gray-100 text-gray-400"
      }`}
    >
      {isDone ? (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
      ) : isActive ? (
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
      ) : (
        <div className="w-2 h-2 bg-gray-300 rounded-full" />
      )}
      {label}
    </div>
  );
}
