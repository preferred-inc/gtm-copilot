from pydantic import BaseModel
from typing import List, Optional
from app.schemas.analysis import SiteAnalysis
from app.schemas.sync import ImportData


class GenerateRequest(BaseModel):
    url: str
    workspace_path: Optional[str] = None


class TagExplanation(BaseModel):
    name: str
    type: str         # "tag" | "trigger" | "variable"
    reason: str
    priority: str     # "required" | "recommended" | "optional"


class GenerateResult(BaseModel):
    config: ImportData
    explanations: List[TagExplanation]


class GenerateResponse(BaseModel):
    analysis: SiteAnalysis
    config: ImportData
    explanations: List[TagExplanation]
