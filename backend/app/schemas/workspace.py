from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class WorkspaceConnectRequest(BaseModel):
    url: Optional[str] = None
    account_id: Optional[str] = None
    container_id: Optional[str] = None
    workspace_id: Optional[str] = None

class WorkspaceInfo(BaseModel):
    workspace_path: str
    workspace: Dict[str, Any]
    container: Dict[str, Any]

class AccountInfo(BaseModel):
    accountId: str
    name: str
    path: str

class ContainerInfo(BaseModel):
    containerId: str
    name: str
    path: str
    publicId: Optional[str] = None

class WorkspaceSummary(BaseModel):
    workspaceId: str
    name: str
    path: str
