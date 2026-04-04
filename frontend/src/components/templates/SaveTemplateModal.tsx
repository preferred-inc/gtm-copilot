"use client";

import { useState } from "react";
import { api, APIError } from "@/lib/api";
import type { ImportData, TagExplanation, TemplateSaveRequest } from "@/lib/types";

const CATEGORIES = [
  { value: "analytics", label: "アナリティクス" },
  { value: "advertising", label: "広告" },
  { value: "conversion", label: "コンバージョン" },
  { value: "engagement", label: "エンゲージメント" },
  { value: "ecommerce", label: "Eコマース" },
  { value: "custom", label: "カスタム" },
] as const;

interface SaveTemplateModalProps {
  config: ImportData;
  explanations: TagExplanation[];
  onClose: () => void;
  onSaved: () => void;
}

export function SaveTemplateModal({
  config,
  explanations,
  onClose,
  onSaved,
}: SaveTemplateModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<TemplateSaveRequest["category"]>("custom");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSave = async () => {
    if (!name.trim()) {
      setError("テンプレート名を入力してください");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await api.saveTemplate({
        name: name.trim(),
        description: description.trim(),
        category,
        config,
        explanations,
      });
      onSaved();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存に失敗しました");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 p-6">
        <h3 className="text-lg font-semibold mb-4">テンプレートとして保存</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              テンプレート名
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例: マイサイト GA4 + 広告設定"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              説明
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="このテンプレートの用途を簡単に記述"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              カテゴリ
            </label>
            <select
              value={category}
              onChange={(e) =>
                setCategory(e.target.value as TemplateSaveRequest["category"])
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          <div className="text-sm text-gray-500">
            タグ: {config.tags.length} / トリガー: {config.triggers.length} / 変数:{" "}
            {config.variables.length}
          </div>

          {error && (
            <div className="text-sm text-red-600">{error}</div>
          )}
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-100"
          >
            キャンセル
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !name.trim()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>
    </div>
  );
}
