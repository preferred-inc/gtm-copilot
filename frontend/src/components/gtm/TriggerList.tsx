"use client";

import { useState } from "react";
import type { GTMItem } from "@/lib/types";
import { ItemEditor } from "./ItemEditor";

export function TriggerList({ items }: { items: GTMItem[] }) {
  const [selected, setSelected] = useState<GTMItem | null>(null);

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left px-4 py-2">Name</th>
              <th className="text-left px-4 py-2">Type</th>
              <th className="text-left px-4 py-2">Trigger ID</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr
                key={i}
                className="border-t border-gray-100 cursor-pointer hover:bg-gray-50"
                onClick={() => setSelected(item)}
              >
                <td className="px-4 py-2 font-medium">{item.name}</td>
                <td className="px-4 py-2 text-gray-500">{item.type}</td>
                <td className="px-4 py-2 text-gray-400">{String(item.triggerId ?? "")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected && <ItemEditor item={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
