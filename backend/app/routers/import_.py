from fastapi import APIRouter, Depends
from app.dependencies import get_gtm_client
from app.schemas.sync import (
    ImportPreviewRequest, ImportPreviewResponse,
    ImportExecuteRequest, ImportExecuteResponse,
)
from app.services.import_service import ImportService
from gtm_client import GTMClient

router = APIRouter(prefix="/api", tags=["import"])

@router.post("/import/preview", response_model=ImportPreviewResponse)
def import_preview(req: ImportPreviewRequest, client: GTMClient = Depends(get_gtm_client)):
    service = ImportService(client)
    result = service.preview(req.workspace_path, req.data.model_dump())
    return ImportPreviewResponse(**result)

@router.post("/import/execute", response_model=ImportExecuteResponse)
def import_execute(req: ImportExecuteRequest, client: GTMClient = Depends(get_gtm_client)):
    service = ImportService(client)
    result = service.execute(req.workspace_path, req.data.model_dump())
    return ImportExecuteResponse(**result)
