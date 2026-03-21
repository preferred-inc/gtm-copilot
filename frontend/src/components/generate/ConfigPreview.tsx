"use client";

import { useState } from "react";
import type { ImportData, TagExplanation } from "@/lib/types";

interface ConfigPreviewProps {
  config: ImportData;
  explanations: TagExplanation[];
  onApply: (filteredConfig: ImportData) => void;
  onDownload: () => void;
  applying: boolean;
}

const PRIORITY_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  required: { bg: "bg-red-50", text: "text-red-700", label: "必須" },
  recommended: { bg: "bg-yellow-50", text: "text-yellow-700", label: "推奨" },
  optional: { bg: "bg-gray-50", text: "text-gray-500", label: "任意" },
};

export function ConfigPreview({
  config,
  explanations,
  onApply,
  onDownload,
  applying,
}: ConfigPreviewProps) {
  const [selected, setSelected] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    explanations.forEach((e) => {
      initial[e.name] = e.priority !== "optional";
    });
    return initial;
  });

  const toggle = (name: string) => {
    setSelected((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  const handleApply = () => {
    const selectedNames = new Set(
      Object.entries(selected)
        .filter(([, v]) => v)
        .map(([k]) => k)
    );

    const filteredConfig: ImportData = {
      tags: config.tags.filter((t) => selectedNames.has(t.name )),
      triggers: config.triggers.filter((t) => selectedNames.has(t.name )),
      variables: config.variables.filter((v) => selectedNames.has(v.name )),
      built_in_variables: config.built_in_variables,
    };

    // Also include triggers/variables referenced by selected tags but not in explanations
    // (they might be dependencies)
    const explainedNames = new Set(explanations.map((e) => e.name));
    const unexplainedTriggers = config.triggers.filter(
      (t) => !explainedNames.has(t.name )
    );
    const unexplainedVariables = config.variables.filter(
      (v) => !explainedNames.has(v.name )
    );
    filteredConfig.triggers = [
      ...filteredConfig.triggers,
      ...unexplainedTriggers,
    ];
    filteredConfig.variables = [
      ...filteredConfig.variables,
      ...unexplainedVariables,
    ];

    onApply(filteredConfig);
  };

  // Group explanations by type
  const tags = explanations.filter((e) => e.type === "tag");
  const triggers = explanations.filter((e) => e.type === "trigger");
  const variables = explanations.filter((e) => e.type === "variable");

  const renderGroup = (title: string, items: TagExplanation[]) => {
    if (items.length === 0) return null;
    return (
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">{title}</h4>
        <div className="space-y-2">
          {items.map((item) => {
            const style = PRIORITY_STYLES[item.priority] || PRIORITY_STYLES.optional;
            return (
              <label
                key={item.name}
                className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={selected[item.name] ?? false}
                  onChange={() => toggle(item.name)}
                  className="mt-0.5"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{item.name}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-xs ${style.bg} ${style.text}`}
                    >
                      {style.label}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{item.reason}</p>
                </div>
              </label>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-2">生成された設定</h3>
      <p className="text-sm text-gray-500 mb-4">
        適用する設定を選択してください。
      </p>

      {renderGroup("タグ", tags)}
      {renderGroup("トリガー", triggers)}
      {renderGroup("変数", variables)}

      <div className="flex gap-3 mt-6">
        <button
          onClick={handleApply}
          disabled={applying || Object.values(selected).every((v) => !v)}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {applying ? "適用中..." : "GTMに適用"}
        </button>
        <button
          onClick={onDownload}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium"
        >
          JSONダウンロード
        </button>
      </div>
    </div>
  );
}
