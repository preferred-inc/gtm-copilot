"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { TagList } from "@/components/gtm/TagList";
import { TriggerList } from "@/components/gtm/TriggerList";
import { VariableList } from "@/components/gtm/VariableList";

type TabKey = "tags" | "triggers" | "variables" | "built_in_variables";

export default function ExportPage() {
  const params = useParams();
  const workspacePath = decodeURIComponent(params.workspacePath as string);
  const [data, setData] = useState<ExportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<TabKey>("tags");

  useEffect(() => {
    api
      .exportWorkspace(workspacePath)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [workspacePath]);

  if (loading) return <div className="text-gray-500">Loading export data...</div>;
  if (error) return <div className="text-red-600">Error: {error}</div>;
  if (!data) return null;

  const tabs: { key: TabKey; label: string; count: number }[] = [
    { key: "tags", label: "Tags", count: data.tags.length },
    { key: "triggers", label: "Triggers", count: data.triggers.length },
    { key: "variables", label: "Variables", count: data.variables.length },
    { key: "built_in_variables", label: "Built-in Variables", count: data.built_in_variables.length },
  ];

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "gtm-export.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Export</h2>
        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Download JSON
        </button>
      </div>

      <div className="border-b border-gray-200 mb-4">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`pb-2 px-1 text-sm font-medium border-b-2 ${
                activeTab === tab.key
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </nav>
      </div>

      {activeTab === "tags" && <TagList items={data.tags} />}
      {activeTab === "triggers" && <TriggerList items={data.triggers} />}
      {activeTab === "variables" && <VariableList items={data.variables} />}
      {activeTab === "built_in_variables" && <VariableList items={data.built_in_variables} />}
    </div>
  );
}
