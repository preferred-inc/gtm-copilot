"""Template library service — manages preset and custom templates."""

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from app.schemas.template import Template, TemplateMetadata, TemplateSaveRequest
from app.services.template_library.presets import PRESET_TEMPLATES

logger = logging.getLogger(__name__)

CUSTOM_TEMPLATES_DIR = Path(__file__).resolve().parent / "custom"

_SAFE_ID_RE = re.compile(r"^custom-[0-9a-f]{8}$")


def _ensure_custom_dir() -> Path:
    CUSTOM_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    return CUSTOM_TEMPLATES_DIR


def _preset_to_template(raw: dict) -> Template:
    config = raw["config"]
    return Template(
        id=raw["id"],
        name=raw["name"],
        description=raw["description"],
        category=raw["category"],
        site_types=raw.get("site_types", []),
        tags_count=len(config.get("tags", [])),
        triggers_count=len(config.get("triggers", [])),
        variables_count=len(config.get("variables", [])),
        is_preset=True,
        created_at="",
        config=config,
        explanations=raw.get("explanations", []),
    )


def _preset_to_metadata(raw: dict) -> TemplateMetadata:
    config = raw["config"]
    return TemplateMetadata(
        id=raw["id"],
        name=raw["name"],
        description=raw["description"],
        category=raw["category"],
        site_types=raw.get("site_types", []),
        tags_count=len(config.get("tags", [])),
        triggers_count=len(config.get("triggers", [])),
        variables_count=len(config.get("variables", [])),
        is_preset=True,
        created_at="",
    )


def list_templates(
    category: Optional[str] = None,
    site_type: Optional[str] = None,
    query: Optional[str] = None,
) -> list[TemplateMetadata]:
    """Return metadata for all templates, optionally filtered."""
    results: list[TemplateMetadata] = []
    query_lower = query.lower() if query else None

    for raw in PRESET_TEMPLATES:
        if category and raw["category"] != category:
            continue
        if site_type and site_type not in raw.get("site_types", []):
            continue
        if query_lower and not _matches_query(raw, query_lower):
            continue
        results.append(_preset_to_metadata(raw))

    # Load custom templates
    custom_dir = _ensure_custom_dir()
    for fp in sorted(custom_dir.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            meta = TemplateMetadata(**{k: v for k, v in data.items() if k != "config" and k != "explanations"})
        except (json.JSONDecodeError, ValidationError, OSError) as exc:
            logger.warning("Skipping corrupted custom template %s: %s", fp.name, exc)
            continue
        if category and meta.category != category:
            continue
        if site_type and site_type not in meta.site_types:
            continue
        if query_lower and not (
            query_lower in meta.name.lower() or query_lower in meta.description.lower()
        ):
            continue
        results.append(meta)

    return results


def _matches_query(raw: dict, query_lower: str) -> bool:
    return query_lower in raw["name"].lower() or query_lower in raw["description"].lower()


def get_template(template_id: str) -> Optional[Template]:
    """Return a full template by ID."""
    for raw in PRESET_TEMPLATES:
        if raw["id"] == template_id:
            return _preset_to_template(raw)

    if not _SAFE_ID_RE.match(template_id):
        return None

    custom_dir = _ensure_custom_dir()
    fp = custom_dir / f"{template_id}.json"
    if fp.exists():
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            return Template(**data)
        except (json.JSONDecodeError, ValidationError, OSError) as exc:
            logger.warning("Failed to load custom template %s: %s", template_id, exc)

    return None


def save_template(req: TemplateSaveRequest) -> Template:
    """Save a custom template and return it."""
    custom_dir = _ensure_custom_dir()
    template_id = f"custom-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    config = req.config.model_dump()
    template = Template(
        id=template_id,
        name=req.name,
        description=req.description,
        category=req.category,
        site_types=[],
        tags_count=len(config.get("tags", [])),
        triggers_count=len(config.get("triggers", [])),
        variables_count=len(config.get("variables", [])),
        is_preset=False,
        created_at=now,
        config=config,
        explanations=req.explanations,
    )

    fp = custom_dir / f"{template_id}.json"
    fp.write_text(template.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Saved custom template: %s (%s)", template.name, template_id)
    return template


def delete_template(template_id: str) -> bool:
    """Delete a custom template. Returns True if deleted."""
    if not _SAFE_ID_RE.match(template_id):
        return False
    custom_dir = _ensure_custom_dir()
    fp = custom_dir / f"{template_id}.json"
    if fp.exists():
        fp.unlink()
        logger.info("Deleted custom template: %s", template_id)
        return True
    return False
