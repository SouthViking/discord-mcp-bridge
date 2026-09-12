# Hosted authentication

GuildSpan's remote transport is a generic Streamable HTTP MCP server. It uses
the MCP OAuth 2.1 discovery flow implemented by FastMCP, with Discord as the
upstream identity provider. There is no client-specific backend behavior.

## Configuration

Apply migrations, then provide:

```env
DISCORD_BOT_TOKEN=...
DISCORD_BOT_PERMISSIONS=446676716608
DISCORD_ALLOWED_GUILDS=
DATABASE_URL=postgresql://user:password@host:5432/guildspan
GUILDSPAN_AUTH_ENABLED=true
GUILDSPAN_PUBLIC_BASE_URL=https://guildspan.example.com
DISCORD_OAUTH_CLIENT_ID=...
DISCORD_OAUTH_CLIENT_SECRET=...
GUILDSPAN_AUTH_SECRET=...
GUILDSPAN_HTTP_HOST=0.0.0.0
```

`GUILDSPAN_AUTH_SECRET` must contain at least 32 characters and should be
generated from a cryptographically secure random source. The Discord developer
application must contain these exact OAuth redirect URIs:

```text
https://guildspan.example.com/auth/callback
https://guildspan.example.com/onboarding/callback
```

`GUILDSPAN_PUBLIC_BASE_URL` is the origin only; do not append `/mcp`.
`DISCORD_ALLOWED_GUILDS` is optional. Leave it empty for self-service server
installation, or populate it to restrict this deployment to selected server
IDs. `DISCORD_BOT_PERMISSIONS` controls the permission bitfield displayed in
Discord's official install screen.

## Client flow

1. An MCP client connects to `https://guildspan.example.com/mcp`.
2. The unauthenticated response and protected-resource metadata advertise the
   standard OAuth authorization server.
3. The client opens a browser for GuildSpan consent and Discord login.
4. Discord authorizes the `identify` and `guilds` scopes and returns control to
   `/auth/callback`.
5. GuildSpan issues its own audience-bound access token to the MCP client. The
   upstream Discord token and the bot token are not exposed to that client.
6. Guild-scoped tools apply optional operator policy and persisted user access.

## Server onboarding flow

1. The user opens `/servers` and chooses **Continue with Discord**.
2. Discord returns the user's identity and visible servers to GuildSpan.
3. GuildSpan shows each server's real state without changing Discord.
4. For a server without the bot, an owner or member with **Manage Server** is
   sent to Discord's official installation screen with that server locked.
5. Discord returns to `/onboarding/callback`. GuildSpan verifies the same user,
   administrator permission, and live bot access before persisting anything.
6. If the bot is already present, the administrator can activate the server
   directly. A normal member is asked to contact a server administrator.

The onboarding browser session is short-lived, encrypted, HttpOnly, Secure in
production, and protected with signed state plus CSRF validation. It reuses the
Discord identity model; GuildSpan does not create a separate password account.

The read-only `discord_list_guilds` tool discovers visible servers without
creating grants. It reports `authorized`, `ready_to_activate`,
`requires_installation`, `administrator_required`, or `restricted`, plus the
public setup URL.

OAuth guild discovery is intentionally separate from routine authorization.
GuildSpan caches each successful guild list for 30 seconds and coalesces
concurrent requests for the same access token. If Discord returns a `429`, the
service honors `Retry-After` for one retry when the delay is at most five
seconds. Longer or repeated limits are returned to the client with the retry
delay instead of holding the request open.

Compatible clients may use dynamic client registration or client ID metadata
documents. A future GuildSpan web platform can manage grants and configuration
without changing this MCP flow.

## Guild authorization

For every guild-scoped tool call, GuildSpan applies the optional
`DISCORD_ALLOWED_GUILDS` restriction and confirms the authenticated user still
belongs to the server. If an active persisted grant already exists, GuildSpan
checks that specific user/server membership through the installed service bot
and the request proceeds. It does not relist the user's OAuth servers on every
tool call.

When no grant exists, GuildSpan allows a one-time bootstrap only when the user
owns the guild or has Discord's **Manage Server** permission and the service bot
can access the guild. It then records the guild installation and grants that
user access. Revoked grants remain denied unless an eligible administrator
bootstraps the guild again.

Guild discovery itself never performs that bootstrap. Activation through the
web flow or a later eligible guild-scoped tool call records the grant only
after every check succeeds.

## Persistence and secrets

PostgreSQL stores users, guild installations, user grants, and OAuth provider
state. OAuth values are encrypted before storage. The short-lived onboarding
session is stored in an encrypted browser cookie, not in a new account table.
`GUILDSPAN_AUTH_SECRET` signs GuildSpan access tokens and derives encryption,
so rotate it as a coordinated session reset rather than as a transparent
configuration change.

The local `stdio` runtime does not require OAuth or PostgreSQL and retains its
existing operator-controlled behavior.
