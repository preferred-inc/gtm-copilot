from typing import List

from pydantic import BaseModel

from app.schemas.analysis import SiteAnalysis
from app.schemas.generate import TagExplanation
from app.schemas.sync import ImportData


class HistoryEntry(BaseModel):
    id: str
    url: str
    site_type: str
    tags_count: int
    triggers_count: int
    variables_count: int
    created_at: str


class HistoryDetail(HistoryEntry):
    analysis: SiteAnalysis
    config: ImportData
    explanations: List[TagExplanation]


class HistoryListResponse(BaseModel):
    entries: List[HistoryEntry]
    total: int
