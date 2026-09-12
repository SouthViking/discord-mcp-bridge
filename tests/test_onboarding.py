from __future__ import annotations

from typing import Any, cast
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from starlette.applications import Starlette

from guildspan.authorization import (
    MANAGE_GUILD_PERMISSION,
    DiscordGuildOnboarding,
    DiscordOAuthGuild,
    DiscordProfile,
)
from guildspan.config import HostedAuthSettings, Settings
from guildspan.onboarding import OnboardingController


class FakeAuthorizationService:
    def __init__(self) -> None:
        self.guilds = [
            DiscordGuildOnboarding(
                id="90001",
                name="Community",
                icon_url=None,
                owner=False,
                status="requires_installation",
                bot_accessible=False,
            )
        ]
        self.recorded_profiles: list[DiscordProfile] = []
        self.bootstrap_calls: list[tuple[str, str, DiscordProfile]] = []

    async def record_user(self, profile: DiscordProfile) -> None:
        self.recorded_profiles.append(profile)

    async def list_onboarding_guilds(
        self,
        *,
        access_token: str,
        discord_user_id: str,
    ) -> list[DiscordGuildOnboarding]:
        assert access_token == "discord-user-token"
        assert discord_user_id == "10001"
        return self.guilds

    async def bootstrap_onboarding_guild(
        self,
        *,
        guild_id: str,
        access_token: str,
        profile: DiscordProfile,
    ) -> DiscordOAuthGuild:
        self.bootstrap_calls.append((guild_id, access_token, profile))
        return DiscordOAuthGuild(
            id=guild_id,
            name="Community",
            icon_url=None,
            owner=False,
            permissions=MANAGE_GUILD_PERMISSION,
        )


def make_settings(**kwargs: object) -> Settings:
    settings_ctor = cast(Any, Settings)
    defaults: dict[str, object] = {
        "discord_bot_token": "bot-token",
        "DISCORD_BOT_PERMISSIONS": 12345,
    }
    defaults.update(kwargs)
    return cast(Settings, settings_ctor(_env_file=None, **defaults))


def discord_transport(requests: list[httpx.Request]) -> httpx.MockTransport:
    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/v10/oauth2/token":
            return httpx.Response(
                200,
                json={
                    "access_token": "discord-user-token",
                    "expires_in": 3600,
                },
            )
        if request.url.path == "/api/v10/users/@me":
            return httpx.Response(
                200,
                json={
                    "id": "10001",
                    "username": "ada",
                    "global_name": "Ada",
                    "avatar": None,
                },
            )
        return httpx.Response(404)

    return httpx.MockTransport(respond)


def create_app(
    discord_client: httpx.AsyncClient,
) -> tuple[Starlette, FakeAuthorizationService]:
    service = FakeAuthorizationService()
    controller = OnboardingController(
        settings=make_settings(),
        auth_settings=HostedAuthSettings(
            public_base_url="https://guildspan.example.com",
            discord_client_id="discord-app",
            discord_client_secret="oauth-secret",
            auth_secret="x" * 32,
        ),
        authorization_service=cast(Any, service),
        http_client=discord_client,
    )
    return Starlette(routes=controller.routes()), service


async def complete_login(client: httpx.AsyncClient) -> httpx.Response:
    start = await client.get("/onboarding/start")
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    return await client.get(
        "/onboarding/callback",
        params={"state": state, "code": "login-code"},
    )


@pytest.mark.asyncio
async def test_discord_login_creates_secure_session_and_lists_servers() -> None:
    discord_requests: list[httpx.Request] = []
    async with httpx.AsyncClient(
        transport=discord_transport(discord_requests)
    ) as discord_client:
        app, service = create_app(discord_client)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://guildspan.example.com",
            follow_redirects=False,
        ) as client:
            callback = await complete_login(client)
            guilds = await client.get("/api/onboarding/guilds")
            logout = await client.get("/onboarding/logout")
            signed_out = await client.get("/api/onboarding/guilds")

    assert callback.status_code == 303
    assert callback.headers["location"] == "/servers"
    session_cookie = next(
        value
        for value in callback.headers.get_list("set-cookie")
        if value.startswith("guildspan_onboarding_session=")
    )
    assert "HttpOnly" in session_cookie
    assert "Secure" in session_cookie
    assert "SameSite=lax" in session_cookie
    assert service.recorded_profiles[0]["discord_user_id"] == "10001"
    assert guilds.status_code == 200
    payload = guilds.json()
    assert payload["user"]["display_name"] == "Ada"
    assert payload["guilds"][0]["status"] == "requires_installation"
    assert payload["csrf_token"]
    assert logout.status_code == 303
    assert logout.headers["location"] == "/servers"
    assert signed_out.status_code == 401
    assert [request.url.path for request in discord_requests] == [
        "/api/v10/oauth2/token",
        "/api/v10/users/@me",
    ]


@pytest.mark.asyncio
async def test_install_flow_uses_official_bot_oauth_and_bootstraps_guild() -> None:
    discord_requests: list[httpx.Request] = []
    async with httpx.AsyncClient(
        transport=discord_transport(discord_requests)
    ) as discord_client:
        app, service = create_app(discord_client)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://guildspan.example.com",
            follow_redirects=False,
        ) as client:
            await complete_login(client)
            install = await client.get(
                "/onboarding/install",
                params={"guild_id": "90001"},
            )
            install_query = parse_qs(urlsplit(install.headers["location"]).query)
            callback = await client.get(
                "/onboarding/callback",
                params={"state": install_query["state"][0], "code": "install-code"},
            )

    assert install.status_code == 302
    assert install_query["scope"] == ["identify guilds bot"]
    assert install_query["guild_id"] == ["90001"]
    assert install_query["disable_guild_select"] == ["true"]
    assert install_query["integration_type"] == ["0"]
    assert install_query["permissions"] == ["12345"]
    assert callback.status_code == 303
    assert callback.headers["location"] == (
        "/success?source=onboarding&guild=Community"
    )
    assert service.bootstrap_calls[0][0:2] == ("90001", "discord-user-token")
    assert service.bootstrap_calls[0][2]["discord_user_id"] == "10001"


@pytest.mark.asyncio
async def test_ready_server_can_be_activated_with_csrf_protection() -> None:
    async with httpx.AsyncClient(transport=discord_transport([])) as discord_client:
        app, service = create_app(discord_client)
        service.guilds = [
            DiscordGuildOnboarding(
                id="90001",
                name="Community",
                icon_url=None,
                owner=True,
                status="ready_to_activate",
                bot_accessible=True,
            )
        ]
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://guildspan.example.com",
            follow_redirects=False,
        ) as client:
            await complete_login(client)
            guilds = await client.get("/api/onboarding/guilds")
            rejected = await client.post("/api/onboarding/guilds/90001/activate")
            activated = await client.post(
                "/api/onboarding/guilds/90001/activate",
                headers={"X-GuildSpan-CSRF": guilds.json()["csrf_token"]},
            )

    assert rejected.status_code == 403
    assert activated.status_code == 200
    assert activated.json() == {
        "status": "ok",
        "redirect": "/success?source=onboarding&guild=Community",
    }
    assert service.bootstrap_calls[0][0] == "90001"


@pytest.mark.asyncio
async def test_onboarding_rejects_missing_session_and_invalid_state() -> None:
    async with httpx.AsyncClient(transport=discord_transport([])) as discord_client:
        app, _service = create_app(discord_client)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://guildspan.example.com",
            follow_redirects=False,
        ) as client:
            guilds = await client.get("/api/onboarding/guilds")
            callback = await client.get(
                "/onboarding/callback",
                params={"state": "invalid", "code": "code"},
            )

    assert guilds.status_code == 401
    assert guilds.json()["login_url"] == "/onboarding/start"
    assert callback.status_code == 303
    assert callback.headers["location"] == "/error?reason=expired"
