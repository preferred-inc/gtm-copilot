"use client";

import { useEffect, useState } from "react";
import { api, APIError } from "@/lib/api";
import type { Template, TemplateMetadata, ImportData } from "@/lib/types";

const CATEGORIES = [
  { value: "", label: "すべて" },
  { value: "analytics", label: "アナリティクス" },
  { value: "advertising", label: "広告" },
  { value: "conversion", label: "コンバージョン" },
  { value: "engagement", label: "エンゲージメント" },
  { value: "ecommerce", label: "Eコマース" },
  { value: "custom", label: "カスタム" },
] as const;

const CATEGORY_COLORS: Record<string, string> = {
  analytics: "bg-blue-100 text-blue-700",
  advertising: "bg-purple-100 text-purple-700",
  conversion: "bg-green-100 text-green-700",
  engagement: "bg-orange-100 text-orange-700",
  ecommerce: "bg-pink-100 text-pink-700",
  custom: "bg-gray-100 text-gray-700",
};

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<TemplateMetadata[]>([]);
  const [category, setCategory] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Detail / preview
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(
    null
  );
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchTemplates = async (cat?: string, query?: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.listTemplates(cat || undefined, undefined, query || undefined);
      setTemplates(res.templates);
    } catch (e) {
      setError(e instanceof Error ? e.message : "テンプレートの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTemplates(category, searchQuery);
    }, searchQuery ? 300 : 0);
    return () => clearTimeout(timer);
  }, [category, searchQuery]);

  const handleSelect = async (id: string) => {
    setDetailLoading(true);
    setError("");
    try {
      const t = await api.getTemplate(id);
      setSelectedTemplate(t);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "テンプレート詳細の取得に失敗しました"
      );
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDownload = (config: ImportData, name: string) => {
    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${name}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("このテンプレートを削除しますか？")) return;
    try {
      await api.deleteTemplate(id);
      setSelectedTemplate(null);
      fetchTemplates(category);
    } catch (e) {
      setError(e instanceof Error ? e.message : "削除に失敗しました");
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6">テンプレートライブラリ</h2>

      {/* Search & Category filter */}
      <div className="mb-6 space-y-3">
        <input
          type="text"
          placeholder="テンプレートを検索..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((c) => (
            <button
              key={c.value}
              onClick={() => {
                setCategory(c.value);
                setSelectedTemplate(null);
              }}
              className={`px-3 py-1.5 text-sm rounded-full font-medium transition-colors ${
                category === c.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Template list */}
        <div className="lg:col-span-1 space-y-3">
          {loading ? (
            <div className="text-gray-400">読み込み中...</div>
          ) : templates.length === 0 ? (
            <div className="text-gray-400">テンプレートがありません</div>
          ) : (
            templates.map((t) => (
              <button
                key={t.id}
                onClick={() => handleSelect(t.id)}
                className={`w-full text-left p-4 rounded-lg border transition-colors ${
                  selectedTemplate?.id === t.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 bg-white hover:border-gray-300"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      CATEGORY_COLORS[t.category] || CATEGORY_COLORS.custom
                    }`}
                  >
                    {CATEGORIES.find((c) => c.value === t.category)?.label ||
                      t.category}
                  </span>
                  {!t.is_preset && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 font-medium">
                      カスタム
                    </span>
                  )}
                </div>
                <h3 className="font-medium text-gray-900">{t.name}</h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {t.description}
                </p>
                <div className="flex gap-3 mt-2 text-xs text-gray-400">
                  <span>タグ: {t.tags_count}</span>
                  <span>トリガー: {t.triggers_count}</span>
                  <span>変数: {t.variables_count}</span>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Template detail */}
        <div className="lg:col-span-2">
          {detailLoading ? (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-gray-400">
              読み込み中...
            </div>
          ) : selectedTemplate ? (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold">
                    {selectedTemplate.name}
                  </h3>
                  <p className="text-gray-500 mt-1">
                    {selectedTemplate.description}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() =>
                      handleDownload(
                        selectedTemplate.config,
                        selectedTemplate.name
                      )
                    }
                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                  >
                    ダウンロード
                  </button>
                  {!selectedTemplate.is_preset && (
                    <button
                      onClick={() => handleDelete(selectedTemplate.id)}
                      className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-md hover:bg-red-50 font-medium"
                    >
                      削除
                    </button>
                  )}
                </div>
              </div>

              {/* Explanations */}
              {selectedTemplate.explanations.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">
                    含まれる設定
                  </h4>
                  <div className="space-y-2">
                    {selectedTemplate.explanations.map((exp, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 text-sm"
                      >
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

              {/* Config preview */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  設定プレビュー
                </h4>
                <div className="bg-gray-50 border border-gray-200 rounded-md p-4 max-h-96 overflow-auto">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(selectedTemplate.config, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-lg p-8 text-center text-gray-400">
              テンプレートを選択してください
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
