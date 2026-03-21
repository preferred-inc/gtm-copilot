"use client";

import type { SiteAnalysis } from "@/lib/types";

interface AnalysisResultProps {
  analysis: SiteAnalysis;
}

const SITE_TYPE_LABELS: Record<string, string> = {
  ec: "EC サイト",
  saas: "SaaS",
  media: "メディア",
  lp: "ランディングページ",
  corporate: "コーポレート",
};

export function AnalysisResult({ analysis }: AnalysisResultProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">分析結果</h3>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">タイトル:</span>
          <p className="font-medium">{analysis.title}</p>
        </div>
        <div>
          <span className="text-gray-500">サイト種別:</span>
          <p className="font-medium">
            {SITE_TYPE_LABELS[analysis.site_type] || analysis.site_type}
          </p>
        </div>
      </div>

      {analysis.description && (
        <div className="mt-3 text-sm">
          <span className="text-gray-500">説明:</span>
          <p className="text-gray-700">{analysis.description}</p>
        </div>
      )}

      {analysis.existing_tags.length > 0 && (
        <div className="mt-4">
          <span className="text-sm text-gray-500">既存タグ:</span>
          <div className="flex flex-wrap gap-2 mt-1">
            {analysis.existing_tags.map((tag, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
              >
                {tag.name} ({tag.identifier})
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.technology.length > 0 && (
        <div className="mt-4">
          <span className="text-sm text-gray-500">検出テクノロジー:</span>
          <div className="flex flex-wrap gap-2 mt-1">
            {analysis.technology.map((tech, i) => (
              <span
                key={i}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.ecommerce && (
        <div className="mt-4">
          <span className="text-sm text-gray-500">EC情報:</span>
          <div className="flex flex-wrap gap-2 mt-1 text-xs">
            {analysis.ecommerce.platform && (
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded">
                {analysis.ecommerce.platform}
              </span>
            )}
            {analysis.ecommerce.has_product_page && (
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded">
                商品ページ
              </span>
            )}
            {analysis.ecommerce.has_cart && (
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded">
                カート
              </span>
            )}
            {analysis.ecommerce.has_checkout && (
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded">
                決済フロー
              </span>
            )}
          </div>
        </div>
      )}

      {analysis.forms.length > 0 && (
        <div className="mt-4 text-sm">
          <span className="text-gray-500">
            フォーム: {analysis.forms.length}個検出
          </span>
        </div>
      )}

      <div className="mt-4 text-sm">
        <span className="text-gray-500">
          分析ページ数: {analysis.pages_analyzed.length}
        </span>
      </div>
    </div>
  );
}
