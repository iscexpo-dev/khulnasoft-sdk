from __future__ import annotations

import os

from ..cache._context import get_headers
from .token_util import (
    fetch_khulnasoft_oidc_token,
    find_project_info,
    get_khulnasoft_cli_token,
    get_token_payload,
    is_expired,
    load_token,
    save_token,
)


class KhulnasoftOidcTokenError(Exception):
    def __init__(self, message: str, cause: Exception | None = None):
        if cause is not None:
            message = f"{message}: {cause}"
        super().__init__(message)
        self.cause = cause


def get_khulnasoft_oidc_token_sync() -> str:
    # Prefer request header (set via khulnasoft.headers.set_headers middleware),
    # fall back to environment variable like the TypeScript SDK.
    headers = get_headers()
    if headers:
        token_from_header = headers.get("x-khulnasoft-oidc-token")
        if token_from_header:
            return token_from_header

    token_from_env = os.getenv("KHULNASOFT_OIDC_TOKEN")
    if not token_from_env:
        raise KhulnasoftOidcTokenError(
            "The 'x-khulnasoft-oidc-token' header is missing from the request. Do you have the OIDC option enabled in the KhulnaSoft project settings?"
        )
    return token_from_env


async def refresh_token() -> None:
    project = find_project_info()
    project_id: str = project["projectId"]
    team_id = project.get("teamId")

    maybe = load_token(project_id)
    if not maybe or is_expired(get_token_payload(maybe.token)):
        auth_token = get_khulnasoft_cli_token()
        if not auth_token:
            raise KhulnasoftOidcTokenError("Failed to refresh OIDC token: login to KhulnaSoft cli")
        if not project_id:
            raise KhulnasoftOidcTokenError("Failed to refresh OIDC token: project id not found")
        new_token = await fetch_khulnasoft_oidc_token(auth_token, project_id, team_id)
        if not new_token:
            raise KhulnasoftOidcTokenError("Failed to refresh OIDC token")
        save_token(new_token, project_id)
        os.environ["KHULNASOFT_OIDC_TOKEN"] = new_token.token
    else:
        os.environ["KHULNASOFT_OIDC_TOKEN"] = maybe.token


async def get_khulnasoft_oidc_token() -> str:
    token = ""
    err: Exception | None = None
    try:
        token = get_khulnasoft_oidc_token_sync()
    except Exception as e:
        err = e
    try:
        if not token or is_expired(get_token_payload(token)):
            await refresh_token()
            token = get_khulnasoft_oidc_token_sync()
    except Exception as e:
        if err and isinstance(e, Exception) and getattr(err, "message", None):
            e.args = (f"{err}\n{e}",)
        raise KhulnasoftOidcTokenError("Failed to refresh OIDC token", e)
    return token


def decode_oidc_payload(token: str) -> dict:
    return get_token_payload(token)
