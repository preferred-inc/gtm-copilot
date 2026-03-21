import logging
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from gtm_client import GTMClient
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies import get_gtm_client
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.crawler import crawl_site
from app.services.export_service import ExportService
from app.services.generator import generate_gtm_config

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URLはhttp://またはhttps://で始まる必要があります")
    if not parsed.netloc or "." not in parsed.netloc:
        raise HTTPException(status_code=400, detail="有効なURLを入力してください")
    return url


@router.post("/api/generate")
@limiter.limit("10/minute")
async def generate(request: Request, req: GenerateRequest) -> GenerateResponse:
    _validate_url(req.url)

    # 1. Crawl site
    logger.info(f"Starting generation for {req.url}")
    try:
        analysis = await crawl_site(req.url)
    except Exception as e:
        logger.error(f"Crawl failed for {req.url}: {e}")
        raise HTTPException(status_code=422, detail=f"サイトのクロールに失敗しました: {e}")

    # 2. Get existing GTM config for dedup (optional)
    existing = None
    # Note: workspace_path requires auth, so we skip if not provided
    # In future, we can add optional GTMClient dependency

    # 3. AI generation
    logger.info(f"Generating GTM config for {req.url} (site_type={analysis.site_type})")
    try:
        result = await generate_gtm_config(analysis, existing)
    except ValueError as e:
        logger.error(f"Generation failed for {req.url}: {e}")
        raise HTTPException(status_code=500, detail=f"GTM設定の生成に失敗しました: {e}")

    logger.info(f"Generation complete: {len(result.config.tags)} tags, {len(result.config.triggers)} triggers, {len(result.config.variables)} variables")
    return GenerateResponse(
        analysis=analysis,
        config=result.config,
        explanations=result.explanations,
    )


@router.post("/api/generate/with-workspace")
@limiter.limit("10/minute")
async def generate_with_workspace(
    request: Request,
    req: GenerateRequest,
    client: GTMClient = Depends(get_gtm_client),
) -> GenerateResponse:
    _validate_url(req.url)

    # 1. Crawl site
    logger.info(f"Starting generation (with workspace) for {req.url}")
    try:
        analysis = await crawl_site(req.url)
    except Exception as e:
        logger.error(f"Crawl failed for {req.url}: {e}")
        raise HTTPException(status_code=422, detail=f"サイトのクロールに失敗しました: {e}")

    # 2. Get existing GTM config for dedup
    existing = None
    if req.workspace_path:
        try:
            existing = ExportService(client).export_workspace(req.workspace_path)
            logger.info("Loaded existing workspace config for dedup")
        except Exception as e:
            logger.warning(f"Failed to load existing config: {e}")

    # 3. AI generation
    logger.info(f"Generating GTM config for {req.url} (site_type={analysis.site_type})")
    try:
        result = await generate_gtm_config(analysis, existing)
    except ValueError as e:
        logger.error(f"Generation failed for {req.url}: {e}")
        raise HTTPException(status_code=500, detail=f"GTM設定の生成に失敗しました: {e}")

    logger.info(f"Generation complete: {len(result.config.tags)} tags, {len(result.config.triggers)} triggers, {len(result.config.variables)} variables")
    return GenerateResponse(
        analysis=analysis,
        config=result.config,
        explanations=result.explanations,
    )
