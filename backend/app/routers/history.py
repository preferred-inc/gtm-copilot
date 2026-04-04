"""Generation history API endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.history import HistoryDetail, HistoryListResponse
from app.services import history_service

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
def list_history(limit: int = 50, offset: int = 0):
    """生成履歴の一覧を取得する。"""
    entries, total = history_service.list_history(limit=limit, offset=offset)
    return HistoryListResponse(entries=entries, total=total)


@router.get("/{entry_id}", response_model=HistoryDetail)
def get_history(entry_id: str):
    """生成履歴の詳細を取得する。"""
    entry = history_service.get_history(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="履歴が見つかりません")
    return entry


@router.delete("/{entry_id}")
def delete_history(entry_id: str):
    """生成履歴を削除する。"""
    deleted = history_service.delete_history(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="履歴が見つかりません")
    return {"detail": "削除しました"}
