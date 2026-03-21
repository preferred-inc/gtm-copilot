"use client";

import { useState } from "react";
import { ItemEditor } from "./ItemEditor";

export function TagList({ items }: { items: Record<string, unknown>[] }) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left px-4 py-2">Name</th>
              <th className="text-left px-4 py-2">Type</th>
              <th className="text-left px-4 py-2">Tag ID</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr
                key={i}
                className="border-t border-gray-100 cursor-pointer hover:bg-gray-50"
                onClick={() => setSelected(item)}
              >
                <td className="px-4 py-2 font-medium">{item.name as string}</td>
                <td className="px-4 py-2 text-gray-500">{item.type as string}</td>
                <td className="px-4 py-2 text-gray-400">{item.tagId as string}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selected && <ItemEditor item={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
