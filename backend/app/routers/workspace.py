from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.dependencies import get_gtm_client
from app.schemas.workspace import (
    WorkspaceConnectRequest, WorkspaceInfo,
    AccountInfo, ContainerInfo, WorkspaceSummary
)
from gtm_client import GTMClient
from helpers.gtm_utils import parse_gtm_workspace_url

router = APIRouter(prefix="/api", tags=["workspace"])

@router.get("/accounts", response_model=List[AccountInfo])
def list_accounts(client: GTMClient = Depends(get_gtm_client)):
    try:
        accounts = client.list_accounts()
        return [AccountInfo(accountId=a["accountId"], name=a["name"], path=a["path"]) for a in accounts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts/{account_id}/containers", response_model=List[ContainerInfo])
def list_containers(account_id: str, client: GTMClient = Depends(get_gtm_client)):
    try:
        containers = client.list_containers(f"accounts/{account_id}")
        return [ContainerInfo(
            containerId=c["containerId"], name=c["name"], path=c["path"],
            publicId=c.get("publicId")
        ) for c in containers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/containers/{account_id}/{container_id}/workspaces", response_model=List[WorkspaceSummary])
def list_workspaces(account_id: str, container_id: str, client: GTMClient = Depends(get_gtm_client)):
    try:
        container_path = f"accounts/{account_id}/containers/{container_id}"
        workspaces = client.list_workspaces(container_path)
        return [WorkspaceSummary(
            workspaceId=w["workspaceId"], name=w["name"], path=w["path"]
        ) for w in workspaces]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workspace/connect", response_model=WorkspaceInfo)
def connect_workspace(req: WorkspaceConnectRequest, client: GTMClient = Depends(get_gtm_client)):
    account_id = req.account_id
    container_id = req.container_id
    workspace_id = req.workspace_id

    if req.url:
        parsed = parse_gtm_workspace_url(req.url)
        if not parsed:
            raise HTTPException(status_code=400, detail="Invalid GTM workspace URL")
        account_id = parsed["account_id"]
        container_id = parsed["container_id"]
        workspace_id = parsed["workspace_id"]

    if not all([account_id, container_id, workspace_id]):
        raise HTTPException(status_code=400, detail="account_id, container_id, and workspace_id are required")

    container_path = f"accounts/{account_id}/containers/{container_id}"
    workspace_path = f"{container_path}/workspaces/{workspace_id}"

    try:
        container = client.get_container(container_path)
        workspace = client.get_workspace(workspace_path)
        return WorkspaceInfo(
            workspace_path=workspace_path,
            workspace=workspace,
            container=container,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
