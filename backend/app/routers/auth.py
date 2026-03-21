from authentication import exchange_code_for_tokens, get_authorization_url
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import Settings, get_settings
from app.session import create_session, delete_session, get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/login")
def login(settings: Settings = Depends(get_settings)):
    url = get_authorization_url(
        client_id=settings.GTM_CLIENT_ID,
        redirect_uri=settings.OAUTH_REDIRECT_URI,
    )
    return RedirectResponse(url)


@router.get("/callback")
def callback(code: str, request: Request, settings: Settings = Depends(get_settings)):
    tokens = exchange_code_for_tokens(
        code=code,
        client_id=settings.GTM_CLIENT_ID,
        client_secret=settings.GTM_CLIENT_SECRET,
        redirect_uri=settings.OAUTH_REDIRECT_URI,
    )

    session_id = create_session(
        refresh_token=tokens["refresh_token"],
        client_id=settings.GTM_CLIENT_ID,
        client_secret=settings.GTM_CLIENT_SECRET,
    )

    response = RedirectResponse(url=settings.FRONTEND_URL)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    return response


@router.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)

    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie(key="session_id")
    return response


@router.get("/me")
def me(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse(content={"logged_in": False}, status_code=401)

    session = get_session(session_id)
    if not session:
        return JSONResponse(content={"logged_in": False}, status_code=401)

    return {"logged_in": True}
