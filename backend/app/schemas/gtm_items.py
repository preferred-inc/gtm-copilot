from pydantic import BaseModel
from typing import List, Dict, Any

class ExportRequest(BaseModel):
    workspace_path: str

class ExportResponse(BaseModel):
    tags: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    built_in_variables: List[Dict[str, Any]]
