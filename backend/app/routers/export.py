from fastapi import APIRouter, Depends
from app.dependencies import get_gtm_client
from app.schemas.gtm_items import ExportRequest, ExportResponse
from app.services.export_service import ExportService
from gtm_client import GTMClient

router = APIRouter(prefix="/api", tags=["export"])

@router.post("/export", response_model=ExportResponse)
def export_workspace(req: ExportRequest, client: GTMClient = Depends(get_gtm_client)):
    service = ExportService(client)
    result = service.export_workspace(req.workspace_path)
    return ExportResponse(**result)
