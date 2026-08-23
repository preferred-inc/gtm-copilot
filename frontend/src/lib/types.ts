// Workspace
export interface AccountInfo {
  accountId: string;
  name: string;
  path: string;
}

export interface ContainerInfo {
  containerId: string;
  name: string;
  path: string;
  publicId?: string;
}

export interface WorkspaceSummary {
  workspaceId: string;
  name: string;
  path: string;
}

export interface WorkspaceConnectRequest {
  url?: string;
  account_id?: string;
  container_id?: string;
  workspace_id?: string;
}

export interface WorkspaceInfo {
  workspace_path: string;
  workspace: Record<string, unknown>;
  container: Record<string, unknown>;
}

// Export
export interface ExportResponse {
  tags: GTMItem[];
  triggers: GTMItem[];
  variables: GTMItem[];
  built_in_variables: GTMItem[];
}

// GTM item (tag/trigger/variable) — always has name and type
export interface GTMItem {
  name: string;
  type: string;
  [key: string]: unknown;
}

// Import
export interface ImportData {
  tags: GTMItem[];
  triggers: GTMItem[];
  variables: GTMItem[];
  built_in_variables: GTMItem[];
}

export interface DiffItem {
  name: string;
  type: string;
  action: "create" | "update" | "skip";
  remote?: GTMItem;
  local?: GTMItem;
}

export interface ImportPreviewResponse {
  diffs: DiffItem[];
  summary: Record<string, number>;
}

export interface ImportExecuteResult {
  type: string;
  name: string;
  action: "created" | "updated" | "skipped" | "error";
  error?: string;
}

export interface ImportExecuteResponse {
  results: ImportExecuteResult[];
  summary: Record<string, number>;
}

// Generate
export interface ExistingTag {
  name: string;
  type: string;
  identifier: string;
}

export interface FormInfo {
  action: string;
  method: string;
  id: string;
  name: string;
  fields: string[];
}

export interface CTAInfo {
  text: string;
  tag: string;
  href: string;
  classes: string;
}

export interface EcommerceInfo {
  platform: string;
  has_product_page: boolean;
  has_cart: boolean;
  has_checkout: boolean;
  currency: string;
}

export interface PageInfo {
  url: string;
  title: string;
  type: string;
}

export interface SiteAnalysis {
  url: string;
  title: string;
  description: string;
  site_type: "ec" | "saas" | "media" | "lp" | "corporate";
  existing_tags: ExistingTag[];
  forms: FormInfo[];
  cta_elements: CTAInfo[];
  ecommerce: EcommerceInfo | null;
  technology: string[];
  pages_analyzed: PageInfo[];
}

export interface TagExplanation {
  name: string;
  type: "tag" | "trigger" | "variable";
  reason: string;
  priority: "required" | "recommended" | "optional";
}

export interface GenerateResponse {
  analysis: SiteAnalysis;
  config: ImportData;
  explanations: TagExplanation[];
}

// Templates
export interface TemplateMetadata {
  id: string;
  name: string;
  description: string;
  category: "analytics" | "advertising" | "conversion" | "engagement" | "ecommerce" | "custom";
  site_types: string[];
  tags_count: number;
  triggers_count: number;
  variables_count: number;
  is_preset: boolean;
  created_at: string;
}

export interface Template extends TemplateMetadata {
  config: ImportData;
  explanations: TagExplanation[];
}

export interface TemplateListResponse {
  templates: TemplateMetadata[];
}

export interface TemplateSaveRequest {
  name: string;
  description: string;
  category: TemplateMetadata["category"];
  config: ImportData;
  explanations: TagExplanation[];
}

// History
export interface HistoryEntry {
  id: string;
  url: string;
  site_type: string;
  tags_count: number;
  triggers_count: number;
  variables_count: number;
  created_at: string;
}

export interface HistoryDetail extends HistoryEntry {
  analysis: SiteAnalysis;
  config: ImportData;
  explanations: TagExplanation[];
}

export interface HistoryListResponse {
  entries: HistoryEntry[];
  total: number;
}

// API Error
export interface APIErrorResponse {
  detail: string;
  type?: string;
}
