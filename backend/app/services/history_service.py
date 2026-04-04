"""Generation history service — stores and retrieves past generation results."""

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from app.schemas.history import HistoryDetail, HistoryEntry

logger = logging.getLogger(__name__)

HISTORY_DIR = Path(__file__).resolve().parent.parent / "data" / "history"

_SAFE_ID_RE = re.compile(r"^[0-9a-f]{8}$")


def _ensure_dir() -> Path:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    return HISTORY_DIR


def save_generation(url: str, site_type: str, analysis: dict, config: dict, explanations: list) -> HistoryEntry:
    """Save a generation result and return its metadata."""
    history_dir = _ensure_dir()
    entry_id = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc).isoformat()

    detail = {
        "id": entry_id,
        "url": url,
        "site_type": site_type,
        "tags_count": len(config.get("tags", [])),
        "triggers_count": len(config.get("triggers", [])),
        "variables_count": len(config.get("variables", [])),
        "created_at": now,
        "analysis": analysis,
        "config": config,
        "explanations": explanations,
    }

    fp = history_dir / f"{entry_id}.json"
    fp.write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved generation history: %s (%s)", url, entry_id)

    return HistoryEntry(
        id=entry_id,
        url=url,
        site_type=site_type,
        tags_count=detail["tags_count"],
        triggers_count=detail["triggers_count"],
        variables_count=detail["variables_count"],
        created_at=now,
    )


def list_history(limit: int = 50, offset: int = 0) -> tuple[list[HistoryEntry], int]:
    """Return history entries sorted by newest first."""
    history_dir = _ensure_dir()
    files = sorted(history_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    total = len(files)

    entries: list[HistoryEntry] = []
    for fp in files[offset:offset + limit]:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            entries.append(HistoryEntry(
                id=data["id"],
                url=data["url"],
                site_type=data["site_type"],
                tags_count=data["tags_count"],
                triggers_count=data["triggers_count"],
                variables_count=data["variables_count"],
                created_at=data["created_at"],
            ))
        except (json.JSONDecodeError, KeyError, ValidationError) as exc:
            logger.warning("Skipping corrupted history file %s: %s", fp.name, exc)

    return entries, total


def get_history(entry_id: str) -> Optional[HistoryDetail]:
    """Return full history detail by ID."""
    if not _SAFE_ID_RE.match(entry_id):
        return None

    history_dir = _ensure_dir()
    fp = history_dir / f"{entry_id}.json"
    if not fp.exists():
        return None

    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return HistoryDetail(**data)
    except (json.JSONDecodeError, ValidationError, OSError) as exc:
        logger.warning("Failed to load history %s: %s", entry_id, exc)
        return None


def delete_history(entry_id: str) -> bool:
    """Delete a history entry. Returns True if deleted."""
    if not _SAFE_ID_RE.match(entry_id):
        return False

    history_dir = _ensure_dir()
    fp = history_dir / f"{entry_id}.json"
    if fp.exists():
        fp.unlink()
        logger.info("Deleted history: %s", entry_id)
        return True
    return False
