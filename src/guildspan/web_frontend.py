"""GuildSpan web frontend and branded OAuth consent integration."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

if TYPE_CHECKING:
    from guildspan.onboarding import OnboardingController

WEB_DIST_DIRECTORY = Path(__file__).with_name("web_dist")
WEB_INDEX_PATH = WEB_DIST_DIRECTORY / "index.html"
WEB_ASSETS_DIRECTORY = WEB_DIST_DIRECTORY / "assets"
WEB_BRAND_DIRECTORY = WEB_DIST_DIRECTORY / "brand"

GUILDSPAN_CONSENT_CSP = (
    "default-src 'none'; "
    "style-src 'self'; "
    "script-src 'self'; "
    "img-src 'self' data: https:; "
    "connect-src 'self'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'"
)


class RevalidatingStaticFiles(StaticFiles):
    """Serve compiled assets while checking for updates on every navigation."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response


async def serve_frontend(_request: Request) -> Response:
    """Serve the Vue application for public product pages."""

    if not WEB_INDEX_PATH.is_file():
        return JSONResponse(
            {
                "status": "unavailable",
                "message": "GuildSpan web assets have not been built.",
            },
            status_code=503,
        )
    return FileResponse(
        WEB_INDEX_PATH,
        media_type="text/html",
        headers={"Cache-Control": "no-store"},
    )


async def onboarding_unavailable(request: Request) -> Response:
    """Return a friendly local response when hosted onboarding is disabled."""

    if request.url.path.startswith("/api/"):
        return JSONResponse(
            {
                "status": "unavailable",
                "message": "Hosted Discord onboarding is not configured.",
            },
            status_code=503,
            headers={"Cache-Control": "no-store"},
        )
    return RedirectResponse(
        "/error?reason=setup",
        status_code=303,
        headers={"Cache-Control": "no-store"},
    )


def create_frontend_routes(
    *,
    onboarding: OnboardingController | None = None,
) -> list[Route | Mount]:
    """Return exact public routes without shadowing MCP or OAuth endpoints."""

    routes: list[Route | Mount] = [
        Mount(
            "/assets",
            app=RevalidatingStaticFiles(
                directory=WEB_ASSETS_DIRECTORY,
                check_dir=False,
            ),
            name="guildspan-assets",
        ),
        Mount(
            "/brand",
            app=RevalidatingStaticFiles(
                directory=WEB_BRAND_DIRECTORY,
                check_dir=False,
            ),
            name="guildspan-brand",
        ),
        Route("/", endpoint=serve_frontend, methods=["GET"]),
        Route("/servers", endpoint=serve_frontend, methods=["GET"]),
        Route("/connecting", endpoint=serve_frontend, methods=["GET"]),
        Route("/success", endpoint=serve_frontend, methods=["GET"]),
        Route("/error", endpoint=serve_frontend, methods=["GET"]),
    ]
    if onboarding is not None:
        routes.extend(onboarding.routes())
    else:
        routes.extend(
            [
                Route(
                    "/onboarding/start",
                    endpoint=onboarding_unavailable,
                    methods=["GET"],
                ),
                Route(
                    "/onboarding/install",
                    endpoint=onboarding_unavailable,
                    methods=["GET"],
                ),
                Route(
                    "/onboarding/logout",
                    endpoint=onboarding_unavailable,
                    methods=["GET"],
                ),
                Route(
                    "/onboarding/callback",
                    endpoint=onboarding_unavailable,
                    methods=["GET"],
                ),
                Route(
                    "/api/onboarding/guilds",
                    endpoint=onboarding_unavailable,
                    methods=["GET"],
                ),
                Route(
                    "/api/onboarding/guilds/{guild_id:str}/activate",
                    endpoint=onboarding_unavailable,
                    methods=["POST"],
                ),
            ]
        )
    return routes


def install_fastmcp_consent_renderer() -> None:
    """Replace only FastMCP's presentation function, preserving OAuth controls.

    FastMCP retains ownership of transaction lookup, CSRF generation and
    validation, consent cookies, redirects, PKCE, and token issuance. The
    renderer receives only escaped display data and the existing secure form
    fields.
    """

    from fastmcp.server.auth.oauth_proxy import consent as consent_module

    consent_module.create_consent_html = create_consent_html  # type: ignore[attr-defined]


def create_consent_html(
    client_id: str,
    redirect_uri: str,
    scopes: list[str],
    txn_id: str,
    csrf_token: str,
    client_name: str | None = None,
    title: str = "Connect to GuildSpan",
    server_name: str | None = None,
    server_icon_url: str | None = None,
    server_website_url: str | None = None,
    client_website_url: str | None = None,
    csp_policy: str | None = None,
    is_cimd_client: bool = False,
    cimd_domain: str | None = None,
) -> str:
    """Create the Vue-backed GuildSpan OAuth consent document.

    The signature intentionally mirrors FastMCP 3.4's consent renderer. Fields
    that are not presented in the first release remain accepted so the adapter
    stays explicit and easy to verify during dependency upgrades.
    """

    del title, server_icon_url, server_website_url, client_website_url, csp_policy

    config = {
        "clientName": client_name or "AI assistant",
        "clientId": client_id,
        "redirectUri": redirect_uri,
        "scopes": scopes,
        "txnId": txn_id,
        "csrfToken": csrf_token,
        "isVerified": is_cimd_client,
        "verifiedDomain": cimd_domain or "",
    }
    serialized_config = html.escape(
        json.dumps(config, ensure_ascii=True, separators=(",", ":")).replace(
            "<", "\\u003c"
        ),
        quote=True,
    )
    escaped_server_name = html.escape(server_name or "GuildSpan")
    escaped_txn_id = html.escape(txn_id, quote=True)
    escaped_csrf_token = html.escape(csrf_token, quote=True)

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light" />
    <link rel="icon" type="image/png" href="/brand/icon.png" />
    <link rel="stylesheet" href="/assets/style.css" />
    <title>Connect to {escaped_server_name}</title>
  </head>
  <body>
    <div id="guildspan-consent" data-config="{serialized_config}"></div>
    <noscript>
      <main class="consent-fallback">
        <img src="/brand/icon.png" alt="GuildSpan" width="56" height="56" />
        <h1>Connect to GuildSpan</h1>
        <p>JavaScript is unavailable. You can still approve this secure connection.</p>
        <form method="POST" action="">
          <input type="hidden" name="txn_id" value="{escaped_txn_id}" />
          <input type="hidden" name="csrf_token" value="{escaped_csrf_token}" />
          <input type="hidden" name="submit" value="true" />
          <button type="submit" name="action" value="approve">Continue to Discord</button>
          <button type="submit" name="action" value="deny">Cancel</button>
        </form>
      </main>
    </noscript>
    <script type="module" src="/assets/consent.js"></script>
  </body>
</html>"""
