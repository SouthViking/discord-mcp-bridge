"""Hosted Discord guild discovery tools."""

from __future__ import annotations

from fastmcp.server.dependencies import get_access_token

from guildspan.errors import DiscordConfigurationError
from guildspan.tools._common import _hosted_authorization


async def discord_list_guilds() -> dict[str, object]:
    """List visible guilds with their current hosted onboarding status."""

    token = get_access_token()
    if token is None:
        raise DiscordConfigurationError(
            "discord_list_guilds requires the hosted MCP runtime with OAuth."
        )

    service = _hosted_authorization()
    guilds = await service.list_onboarding_guilds_for_token(token=token)
    setup_url = (
        f"{service.public_base_url}/servers" if service.public_base_url else None
    )
    return {
        "status": "ok",
        "count": len(guilds),
        "setup_url": setup_url,
        "guilds": [
            {
                "id": guild.id,
                "name": guild.name,
                "icon_url": guild.icon_url,
                "owner": guild.owner,
                "authorization_status": guild.status,
                "bot_accessible": guild.bot_accessible,
            }
            for guild in guilds
        ],
    }
