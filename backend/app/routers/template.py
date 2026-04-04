"""Template library API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.template import Template, TemplateListResponse, TemplateSaveRequest
from app.services.template_library import service as template_service

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=TemplateListResponse)
def list_templates(
    category: Optional[str] = None,
    site_type: Optional[str] = None,
    q: Optional[str] = None,
):
    """テンプレート一覧を取得する（フィルター・検索可能）。"""
    templates = template_service.list_templates(category=category, site_type=site_type, query=q)
    return TemplateListResponse(templates=templates)


@router.get("/{template_id}", response_model=Template)
def get_template(template_id: str):
    """テンプレートの詳細を取得する。"""
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    return template


@router.post("", response_model=Template, status_code=201)
def save_template(req: TemplateSaveRequest):
    """カスタムテンプレートを保存する。"""
    return template_service.save_template(req)


@router.delete("/{template_id}")
def delete_template(template_id: str):
    """カスタムテンプレートを削除する。"""
    if not template_id.startswith("custom-"):
        raise HTTPException(status_code=400, detail="プリセットテンプレートは削除できません")
    deleted = template_service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    return {"detail": "削除しました"}
