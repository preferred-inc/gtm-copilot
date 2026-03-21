from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ImportData(BaseModel):
    tags: List[Dict[str, Any]] = []
    triggers: List[Dict[str, Any]] = []
    variables: List[Dict[str, Any]] = []
    built_in_variables: List[Dict[str, Any]] = []

class ImportPreviewRequest(BaseModel):
    workspace_path: str
    data: ImportData

class DiffItem(BaseModel):
    name: str
    type: str  # "tags", "triggers", "variables", "built_in_variables"
    action: str  # "create", "update", "skip"
    remote: Optional[Dict[str, Any]] = None
    local: Optional[Dict[str, Any]] = None

class ImportPreviewResponse(BaseModel):
    diffs: List[DiffItem]
    summary: Dict[str, int]  # {"create": N, "update": N, "skip": N}

class ImportExecuteRequest(BaseModel):
    workspace_path: str
    data: ImportData

class ImportExecuteResult(BaseModel):
    type: str
    name: str
    action: str  # "created", "updated", "skipped", "error"
    error: Optional[str] = None

class ImportExecuteResponse(BaseModel):
    results: List[ImportExecuteResult]
    summary: Dict[str, int]
