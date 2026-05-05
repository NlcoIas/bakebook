from fastapi import HTTPException, Request

from app.config import settings

CF_ACCESS_HEADER = "Cf-Access-Authenticated-User-Email"


def get_current_user(request: Request) -> str:
    """Extract authenticated user email from Cloudflare Access header.

    In dev mode, returns the configured dev email.
    In prod, returns 401 if the header is missing.
    """
    if settings.env == "dev":
        return request.headers.get(CF_ACCESS_HEADER, settings.auth_dev_email)

    email = request.headers.get(CF_ACCESS_HEADER)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return email
