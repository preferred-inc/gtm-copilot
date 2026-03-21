from fastapi import Depends, Request, HTTPException
from app.config import Settings, get_settings
from app.session import get_session

# Import from existing code (path set in __init__.py)
from gtm_client import GTMClient

def get_gtm_client(request: Request, settings: Settings = Depends(get_settings)) -> GTMClient:
    # 1. Try session cookie first
    session_id = request.cookies.get("session_id")
    if session_id:
        session = get_session(session_id)
        if session:
            return GTMClient(
                refresh_token=session["refresh_token"],
                client_id=session["client_id"],
                client_secret=session["client_secret"],
            )

    # 2. Fallback to header-based credentials (API direct usage)
    client_id = request.headers.get("X-GTM-Client-Id") or settings.GTM_CLIENT_ID
    client_secret = request.headers.get("X-GTM-Client-Secret") or settings.GTM_CLIENT_SECRET
    refresh_token = request.headers.get("X-GTM-Refresh-Token") or settings.GTM_REFRESH_TOKEN

    if not all([client_id, client_secret, refresh_token]):
        raise HTTPException(status_code=401, detail="Not authenticated")

    return GTMClient(
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
    )
