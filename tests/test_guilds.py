from __future__ import annotations

from typing import Any, cast

import pytest
from fastmcp.server.auth import AccessToken

from guildspan.authorization import DiscordGuildOnboarding
from guildspan.errors import DiscordConfigurationError
from guildspan.tools import guilds as guilds_module


class FakeAuthorizationService:
    def __init__(self) -> None:
        self.tokens: list[AccessToken] = []
        self.public_base_url = "https://guildspan.example.com"

    async def list_onboarding_guilds_for_token(
        self,
        *,
        token: AccessToken,
    ) -> list[DiscordGuildOnboarding]:
        self.tokens.append(token)
        return [
            DiscordGuildOnboarding(
                id="guild-1",
                name="Guild One",
                icon_url="https://example.com/icon.png",
                owner=True,
                status="authorized",
                bot_accessible=True,
            ),
            DiscordGuildOnboarding(
                id="guild-2",
                name="Guild Two",
                icon_url=None,
                owner=False,
                status="administrator_required",
                bot_accessible=False,
            ),
        ]


def access_token() -> AccessToken:
    return AccessToken(
        token="discord-user-token",
        client_id="discord-app",
        scopes=["identify", "guilds"],
        claims={"sub": "user-1"},
    )


@pytest.mark.asyncio
async def test_discord_list_guilds_returns_safe_authorization_states(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = access_token()
    service = FakeAuthorizationService()
    monkeypatch.setattr(guilds_module, "get_access_token", lambda: token)
    monkeypatch.setattr(
        guilds_module,
        "_hosted_authorization",
        lambda: cast(Any, service),
    )

    result = await guilds_module.discord_list_guilds()

    assert result == {
        "status": "ok",
        "count": 2,
        "setup_url": "https://guildspan.example.com/servers",
        "guilds": [
            {
                "id": "guild-1",
                "name": "Guild One",
                "icon_url": "https://example.com/icon.png",
                "owner": True,
                "authorization_status": "authorized",
                "bot_accessible": True,
            },
            {
                "id": "guild-2",
                "name": "Guild Two",
                "icon_url": None,
                "owner": False,
                "authorization_status": "administrator_required",
                "bot_accessible": False,
            },
        ],
    }
    assert service.tokens == [token]


@pytest.mark.asyncio
async def test_discord_list_guilds_requires_hosted_oauth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(guilds_module, "get_access_token", lambda: None)

    with pytest.raises(DiscordConfigurationError, match="hosted MCP runtime"):
        await guilds_module.discord_list_guilds()
