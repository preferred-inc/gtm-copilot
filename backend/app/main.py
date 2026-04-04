import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.routers import auth, export, generate, history, import_, template, workspace

settings = get_settings()

# Warn about missing required settings at startup
_missing = settings.validate_required()
if _missing:
    import sys
    msg = f"Missing required environment variables: {', '.join(_missing)}"
    if settings.is_production:
        print(f"FATAL: {msg}", file=sys.stderr)
        sys.exit(1)
    else:
        logging.getLogger(__name__).warning(msg)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="GTM Copilot API",
    version="0.1.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)
app.state.limiter = limiter


def _error_response(status_code: int, detail: str, error_type: str = "error") -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "type": error_type},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return _error_response(429, "リクエスト数が上限を超えました。しばらく待ってから再試行してください。", "rate_limit")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detail = "; ".join(f"{e['loc'][-1]}: {e['msg']}" for e in errors) if errors else "入力が不正です"
    return _error_response(422, detail, "validation_error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return _error_response(exc.status_code, exc.detail, "http_error")
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    detail = "内部エラーが発生しました" if settings.is_production else str(exc)
    return _error_response(500, detail, "internal_error")


# CORS configuration
cors_origins = (
    [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    if settings.CORS_ORIGINS
    else [settings.FRONTEND_URL]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        if request.url.path != "/api/health":
            logger.info(
                "%s %s %d %.0fms",
                request.method, request.url.path, response.status_code, duration_ms,
            )
        return response

app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(export.router)
app.include_router(import_.router)
app.include_router(generate.router)
app.include_router(template.router)
app.include_router(history.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
