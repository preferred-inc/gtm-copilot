import type {
  AccountInfo,
  APIErrorResponse,
  ContainerInfo,
  ExportResponse,
  GenerateResponse,
  HistoryDetail,
  HistoryListResponse,
  ImportData,
  ImportExecuteResponse,
  ImportPreviewResponse,
  Template,
  TemplateListResponse,
  TemplateSaveRequest,
  WorkspaceConnectRequest,
  WorkspaceInfo,
  WorkspaceSummary,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public type?: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const error: APIErrorResponse = await res
      .json()
      .catch(() => ({ detail: res.statusText }));
    throw new APIError(error.detail || "API error", res.status, error.type);
  }
  return res.json();
}

export const api = {
  // Workspace
  listAccounts: () => request<AccountInfo[]>("/api/accounts"),
  listContainers: (accountId: string) =>
    request<ContainerInfo[]>(`/api/accounts/${accountId}/containers`),
  listWorkspaces: (accountId: string, containerId: string) =>
    request<WorkspaceSummary[]>(
      `/api/containers/${accountId}/${containerId}/workspaces`,
    ),
  connectWorkspace: (body: WorkspaceConnectRequest) =>
    request<WorkspaceInfo>("/api/workspace/connect", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Export
  exportWorkspace: (workspacePath: string) =>
    request<ExportResponse>("/api/export", {
      method: "POST",
      body: JSON.stringify({ workspace_path: workspacePath }),
    }),

  // Import
  importPreview: (workspacePath: string, data: ImportData) =>
    request<ImportPreviewResponse>("/api/import/preview", {
      method: "POST",
      body: JSON.stringify({ workspace_path: workspacePath, data }),
    }),
  importExecute: (workspacePath: string, data: ImportData) =>
    request<ImportExecuteResponse>("/api/import/execute", {
      method: "POST",
      body: JSON.stringify({ workspace_path: workspacePath, data }),
    }),

  // Generate (longer timeout: 3 min for crawl + AI)
  generate: (url: string) =>
    request<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify({ url }),
      signal: AbortSignal.timeout(180_000),
    }),
  generateWithWorkspace: (url: string, workspacePath: string) =>
    request<GenerateResponse>("/api/generate/with-workspace", {
      method: "POST",
      body: JSON.stringify({ url, workspace_path: workspacePath }),
      signal: AbortSignal.timeout(180_000),
    }),

  // Templates
  listTemplates: (category?: string, siteType?: string, query?: string) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (siteType) params.set("site_type", siteType);
    if (query) params.set("q", query);
    const qs = params.toString();
    return request<TemplateListResponse>(`/api/templates${qs ? `?${qs}` : ""}`);
  },
  getTemplate: (id: string) => request<Template>(`/api/templates/${id}`),
  saveTemplate: (body: TemplateSaveRequest) =>
    request<Template>("/api/templates", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  deleteTemplate: (id: string) =>
    request<{ detail: string }>(`/api/templates/${id}`, { method: "DELETE" }),

  // History
  listHistory: (limit = 50, offset = 0) =>
    request<HistoryListResponse>(`/api/history?limit=${limit}&offset=${offset}`),
  getHistory: (id: string) => request<HistoryDetail>(`/api/history/${id}`),
  deleteHistory: (id: string) =>
    request<{ detail: string }>(`/api/history/${id}`, { method: "DELETE" }),
};
