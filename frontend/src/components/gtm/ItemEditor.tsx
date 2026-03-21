"use client";

import type { GTMItem } from "@/lib/types";

export function ItemEditor({
  item,
  onClose,
}: {
  item: GTMItem;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h3 className="font-semibold">{item.name || "Detail"}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">
            &times;
          </button>
        </div>
        <div className="overflow-auto p-4">
          <pre className="text-xs bg-gray-50 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(item, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
