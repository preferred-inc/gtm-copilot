import json
import logging
import os
from typing import Any, Dict, List, Optional

import anthropic

from app.schemas.analysis import SiteAnalysis
from app.schemas.generate import GenerateResult, TagExplanation
from app.schemas.sync import ImportData
from app.services.templates.prompts import (
    SITE_TYPE_GUIDELINES,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    get_detection_guidelines,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def generate_gtm_config(
    analysis: SiteAnalysis,
    existing_config: Optional[Dict[str, Any]] = None,
) -> GenerateResult:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")
    client = anthropic.AsyncAnthropic(api_key=api_key)

    user_prompt = _build_user_prompt(analysis, existing_config)

    for attempt in range(MAX_RETRIES):
        try:
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
                system=SYSTEM_PROMPT,
            )

            raw_text = message.content[0].text
            parsed = _parse_response(raw_text)

            config = ImportData(**parsed["config"])
            explanations = [TagExplanation(**e) for e in parsed["explanations"]]

            errors = validate_generated_config(config)
            if errors:
                logger.warning(f"Validation errors (attempt {attempt + 1}): {errors}")
                if attempt < MAX_RETRIES - 1:
                    continue
                raise ValueError(f"Generated config validation failed: {errors}")

            return GenerateResult(config=config, explanations=explanations)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Parse error (attempt {attempt + 1}): {e}")
            if attempt >= MAX_RETRIES - 1:
                raise ValueError(f"Failed to parse LLM response after {MAX_RETRIES} attempts: {e}")

    raise ValueError("Failed to generate GTM config")


def _build_user_prompt(
    analysis: SiteAnalysis,
    existing_config: Optional[Dict[str, Any]],
) -> str:
    site_type = analysis.site_type
    guidelines = SITE_TYPE_GUIDELINES.get(site_type, SITE_TYPE_GUIDELINES["corporate"])
    detection = get_detection_guidelines(analysis)

    existing_str = "なし（新規設定）"
    if existing_config:
        existing_str = json.dumps(existing_config, indent=2, ensure_ascii=False)

    return USER_PROMPT_TEMPLATE.format(
        site_analysis=analysis.model_dump_json(indent=2),
        existing_config=existing_str,
        site_type=site_type,
        site_type_guidelines=guidelines,
        detection_guidelines=detection,
    )


def _parse_response(raw_text: str) -> dict:
    # Try to extract JSON from markdown code block
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1]
        text = text.split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        text = text.split("```", 1)[0]

    return json.loads(text.strip())


def validate_generated_config(data: ImportData) -> List[str]:
    errors = []

    for tag in data.tags:
        if "name" not in tag:
            errors.append(f"Tag missing 'name': {tag}")
        if "type" not in tag:
            errors.append(f"Tag missing 'type': {tag.get('name', 'unknown')}")
        # Reject arbitrary Custom HTML
        if tag.get("type") == "html":
            params = tag.get("parameter", [])
            for p in params:
                if p.get("key") == "html" and "<script" in str(p.get("value", "")).lower():
                    errors.append(f"Tag '{tag.get('name')}' contains prohibited Custom HTML with <script>")

    for trigger in data.triggers:
        if "name" not in trigger:
            errors.append(f"Trigger missing 'name': {trigger}")
        if "type" not in trigger:
            errors.append(f"Trigger missing 'type': {trigger.get('name', 'unknown')}")

    for variable in data.variables:
        if "name" not in variable:
            errors.append(f"Variable missing 'name': {variable}")
        if "type" not in variable:
            errors.append(f"Variable missing 'type': {variable.get('name', 'unknown')}")

    return errors
