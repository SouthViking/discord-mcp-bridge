from __future__ import annotations

import html
import json
import re

import httpx
import pytest

from guildspan.app import create_http_app
from guildspan.web_frontend import (
    create_consent_html,
    install_fastmcp_consent_renderer,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    ["/", "/servers", "/connecting", "/success", "/error"],
)
async def test_frontend_routes_serve_vue_application(path: str) -> None:
    transport = httpx.ASGITransport(app=create_http_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get(path)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<div id="app"></div>' in response.text
    assert re.search(r"/assets/app-[A-Za-z0-9_-]+\.js", response.text)


@pytest.mark.asyncio
async def test_local_runtime_reports_that_hosted_onboarding_is_unavailable() -> None:
    transport = httpx.ASGITransport(app=create_http_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        api_response = await client.get("/api/onboarding/guilds")
        start_response = await client.get("/onboarding/start")

    assert api_response.status_code == 503
    assert api_response.json()["status"] == "unavailable"
    assert start_response.status_code == 303
    assert start_response.headers["location"] == "/error?reason=setup"


@pytest.mark.asyncio
async def test_frontend_serves_brand_and_compiled_assets() -> None:
    transport = httpx.ASGITransport(app=create_http_app())
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        icon_response = await client.get("/brand/icon.png")
        script_response = await client.get("/assets/consent.js")

    assert icon_response.status_code == 200
    assert icon_response.headers["content-type"] == "image/png"
    assert icon_response.headers["cache-control"] == "no-cache"
    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert script_response.headers["cache-control"] == "no-cache"


def test_consent_document_contains_secure_form_and_escaped_configuration() -> None:
    malicious_client_name = '</div><script>alert("unsafe")</script>'
    document = create_consent_html(
        client_id='client"><img src=x onerror=alert(1)>',
        redirect_uri="https://assistant.example/callback?next=<unsafe>",
        scopes=["identify", "guilds"],
        txn_id='txn"><script>bad()</script>',
        csrf_token='csrf"><script>bad()</script>',
        client_name=malicious_client_name,
        server_name="GuildSpan <Preview>",
    )

    assert '<script type="module" src="/assets/consent.js"></script>' in document
    assert '<link rel="stylesheet" href="/assets/style.css" />' in document
    assert 'name="txn_id"' in document
    assert 'name="csrf_token"' in document
    assert 'name="action" value="approve"' in document
    assert 'name="action" value="deny"' in document
    assert malicious_client_name not in document
    assert '<script>alert("unsafe")</script>' not in document
    assert "GuildSpan &lt;Preview&gt;" in document

    expected_config = html.escape(
        json.dumps(
            {
                "clientName": malicious_client_name,
                "clientId": 'client"><img src=x onerror=alert(1)>',
                "redirectUri": "https://assistant.example/callback?next=<unsafe>",
                "scopes": ["identify", "guilds"],
                "txnId": 'txn"><script>bad()</script>',
                "csrfToken": 'csrf"><script>bad()</script>',
                "isVerified": False,
                "verifiedDomain": "",
            },
            ensure_ascii=True,
            separators=(",", ":"),
        ).replace("<", "\\u003c"),
        quote=True,
    )
    assert f'data-config="{expected_config}"' in document


def test_consent_document_uses_generic_client_fallback() -> None:
    document = create_consent_html(
        client_id="assistant-client",
        redirect_uri="https://assistant.example/callback",
        scopes=["identify", "guilds"],
        txn_id="transaction",
        csrf_token="csrf-token",
    )

    assert "clientName&quot;:&quot;AI assistant" in document
    assert "Codex" not in document


def test_install_consent_renderer_patches_only_fastmcp_presentation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fastmcp.server.auth.oauth_proxy import consent as consent_module

    def placeholder_renderer() -> str:
        return "original"

    monkeypatch.setattr(consent_module, "create_consent_html", placeholder_renderer)

    install_fastmcp_consent_renderer()

    assert vars(consent_module)["create_consent_html"] is create_consent_html
