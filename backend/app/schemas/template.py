from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from app.schemas.sync import ImportData


class TemplateMetadata(BaseModel):
    id: str
    name: str
    description: str
    category: Literal[
        "analytics", "advertising", "conversion", "engagement", "ecommerce", "custom"
    ]
    site_types: List[str] = []  # ec, saas, media, lp, corporate
    tags_count: int = 0
    triggers_count: int = 0
    variables_count: int = 0
    is_preset: bool = True
    created_at: str = ""


class Template(TemplateMetadata):
    config: ImportData
    explanations: List[Dict[str, Any]] = []


class TemplateListResponse(BaseModel):
    templates: List[TemplateMetadata]


class TemplateSaveRequest(BaseModel):
    name: str
    description: str
    category: Literal[
        "analytics", "advertising", "conversion", "engagement", "ecommerce", "custom"
    ] = "custom"
    config: ImportData
    explanations: List[Dict[str, Any]] = []
