"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { HistoryEntry, HistoryDetail } from "@/lib/types";

const SITE_TYPE_LABELS: Record<string, string> = {
  ec: "ECサイト",
  saas: "SaaS",
  media: "メディア",
  lp: "LP",
  corporate: "コーポレート",
};

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selected, setSelected] = useState<HistoryDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.listHistory();
      setEntries(res.entries);
      setTotal(res.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "履歴の取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSelect = async (id: string) => {
    setDetailLoading(true);
    setError("");
    try {
      const detail = await api.getHistory(id);
      setSelected(detail);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "履歴詳細の取得に失敗しました"
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("この履歴を削除しますか？")) return;
    try {
      await api.deleteHistory(id);
      setSelected(null);
      fetchHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "削除に失敗しました");
    }
  };

  const handleDownload = (detail: HistoryDetail) => {
    const blob = new Blob([JSON.stringify(detail.config, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gtm-config-${detail.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleString("ja-JP", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">生成履歴</h2>
        <span className="text-sm text-gray-500">{total}件</span>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Entry list */}
        <div className="lg:col-span-1 space-y-3">
          {loading ? (
            <div className="text-gray-400">読み込み中...</div>
          ) : entries.length === 0 ? (
            <div className="text-gray-400">
              まだ生成履歴がありません。AI生成ページで設定を生成すると、ここに履歴が表示されます。
            </div>
          ) : (
            entries.map((entry) => (
              <button
                key={entry.id}
                onClick={() => handleSelect(entry.id)}
                className={`w-full text-left p-4 rounded-lg border transition-colors ${
                  selected?.id === entry.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 bg-white hover:border-gray-300"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">
                    {SITE_TYPE_LABELS[entry.site_type] || entry.site_type}
                  </span>
                  <span className="text-xs text-gray-400">
                    {formatDate(entry.created_at)}
                  </span>
                </div>
                <h3 className="font-medium text-gray-900 truncate">
                  {entry.url}
                </h3>
                <div className="flex gap-3 mt-2 text-xs text-gray-400">
                  <span>タグ: {entry.tags_count}</span>
                  <span>トリガー: {entry.triggers_count}</span>
                  <span>変数: {entry.variables_count}</span>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Detail */}
        <div className="lg:col-span-2">
          {detailLoading ? (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-gray-400">
              読み込み中...
            </div>
          ) : selected ? (
            <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-semibold break-all">
                    {selected.url}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {SITE_TYPE_LABELS[selected.site_type] || selected.site_type}{" "}
                    &middot; {formatDate(selected.created_at)}
                  </p>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleDownload(selected)}
                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                  >
                    ダウンロード
                  </button>
                  <button
                    onClick={() => handleDelete(selected.id)}
                    className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-md hover:bg-red-50 font-medium"
                  >
                    削除
                  </button>
                </div>
              </div>

              {/* Analysis summary */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  サイト分析結果
                </h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-gray-50 p-3 rounded-md">
                    <span className="text-gray-500">タイトル</span>
                    <p className="font-medium">{selected.analysis.title || "-"}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <span className="text-gray-500">検出テクノロジー</span>
                    <p className="font-medium">
                      {selected.analysis.technology.length > 0
                        ? selected.analysis.technology.join(", ")
                        : "-"}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <span className="text-gray-500">フォーム数</span>
                    <p className="font-medium">{selected.analysis.forms.length}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <span className="text-gray-500">CTA数</span>
                    <p className="font-medium">
                      {selected.analysis.cta_elements.length}
                    </p>
                  </div>
                </div>
              </div>

              {/* Explanations */}
              {selected.explanations.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">
                    生成された設定 ({selected.tags_count}タグ / {selected.triggers_count}トリガー / {selected.variables_count}変数)
                  </h4>
                  <div className="space-y-2">
                    {selected.explanations.map((exp, i) => (
                      <div key={i} className="flex items-start gap-3 text-sm">
                        <span
                          className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium ${
                            exp.priority === "required"
                              ? "bg-red-100 text-red-700"
                              : exp.priority === "recommended"
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {exp.type === "tag"
                            ? "タグ"
                            : exp.type === "trigger"
                              ? "トリガー"
                              : "変数"}
                        </span>
                        <div>
                          <span className="font-medium text-gray-800">
                            {exp.name}
                          </span>
                          <span className="text-gray-500 ml-2">
                            {exp.reason}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Config JSON */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  設定JSON
                </h4>
                <div className="bg-gray-50 border border-gray-200 rounded-md p-4 max-h-96 overflow-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(selected.config, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-center text-gray-400">
              履歴を選択してください
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
