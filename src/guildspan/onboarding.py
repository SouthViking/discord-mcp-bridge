"""Discord-backed web onboarding for GuildSpan server installations."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from dataclasses import asdict
from typing import TypedDict, cast
from urllib.parse import urlencode, urlsplit

import httpx
from cryptography.fernet import Fernet, InvalidToken
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Route

from guildspan.authorization import DiscordProfile, GuildAuthorizationService
from guildspan.config import HostedAuthSettings, Settings
from guildspan.errors import DiscordApiError, DiscordPermissionError

DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/v10/oauth2/token"
DISCORD_CURRENT_USER_URL = "https://discord.com/api/v10/users/@me"
ONBOARDING_CALLBACK_PATH = "/onboarding/callback"
ONBOARDING_SESSION_COOKIE = "guildspan_onboarding_session"
ONBOARDING_STATE_COOKIE = "guildspan_onboarding_state"
ONBOARDING_STATE_TTL_SECONDS = 10 * 60
ONBOARDING_SESSION_TTL_SECONDS = 60 * 60
ONBOARDING_COOKIE_SALT = b"guildspan-onboarding-cookie-v1"


class _StatePayload(TypedDict):
    nonce: str
    intent: str
    guild_id: str
    user_id: str
    expires_at: int


class _SessionPayload(TypedDict):
    access_token: str
    discord_user_id: str
    username: str | None
    display_name: str | None
    avatar_url: str | None
    csrf_token: str
    expires_at: int


class OnboardingController:
    """Serve a short-lived Discord login and guild installation workflow."""

    def __init__(
        self,
        *,
        settings: Settings,
        auth_settings: HostedAuthSettings,
        authorization_service: GuildAuthorizationService,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._settings = settings
        self._auth_settings = auth_settings
        self._authorization_service = authorization_service
        self._http_client = http_client
        self._secure_cookies = urlsplit(auth_settings.public_base_url).scheme == "https"
        digest = hashlib.sha256(
            auth_settings.auth_secret.encode("utf-8") + ONBOARDING_COOKIE_SALT
        ).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(digest))

    def routes(self) -> list[Route]:
        """Return exact onboarding routes for the hosted application."""

        return [
            Route(
                "/onboarding/start",
                endpoint=self.start,
                methods=["GET"],
            ),
            Route(
                "/onboarding/install",
                endpoint=self.install,
                methods=["GET"],
            ),
            Route(
                "/onboarding/logout",
                endpoint=self.logout,
                methods=["GET"],
            ),
            Route(
                ONBOARDING_CALLBACK_PATH,
                endpoint=self.callback,
                methods=["GET"],
            ),
            Route(
                "/api/onboarding/guilds",
                endpoint=self.list_guilds,
                methods=["GET"],
            ),
            Route(
                "/api/onboarding/guilds/{guild_id:str}/activate",
                endpoint=self.activate_guild,
                methods=["POST"],
            ),
        ]

    async def start(self, _request: Request) -> Response:
        """Begin a Discord identity login for the server selection page."""

        return self._authorization_redirect(intent="login")

    async def install(self, request: Request) -> Response:
        """Begin Discord's official bot installation for one selected guild."""

        session = self._read_session(request)
        if session is None:
            return self._local_redirect("/onboarding/start")

        guild_id = request.query_params.get("guild_id", "").strip()
        if not _valid_snowflake(guild_id):
            return self._local_redirect("/error?reason=guild")

        try:
            guilds = await self._authorization_service.list_onboarding_guilds(
                access_token=session["access_token"],
                discord_user_id=session["discord_user_id"],
            )
        except (DiscordApiError, DiscordPermissionError, httpx.HTTPError):
            return self._local_redirect("/error?reason=oauth")

        selected = next((guild for guild in guilds if guild.id == guild_id), None)
        if selected is None:
            return self._local_redirect("/error?reason=guild")
        if selected.status == "authorized":
            return self._success_redirect(selected.name)
        if selected.status == "ready_to_activate":
            return self._local_redirect("/servers")
        if selected.status != "requires_installation":
            reason = "restricted" if selected.status == "restricted" else "admin"
            return self._local_redirect(f"/error?reason={reason}")

        return self._authorization_redirect(
            intent="install",
            guild_id=guild_id,
            user_id=session["discord_user_id"],
            install_bot=True,
        )

    async def logout(self, _request: Request) -> Response:
        """Clear the short-lived onboarding session and return to sign-in."""

        response = self._local_redirect("/servers")
        response.delete_cookie(
            ONBOARDING_SESSION_COOKIE,
            path="/",
            secure=self._secure_cookies,
            httponly=True,
            samesite="lax",
        )
        return response

    async def callback(self, request: Request) -> Response:
        """Complete Discord login or bot installation after validating state."""

        error = request.query_params.get("error")
        if error:
            return self._callback_redirect("/error?reason=denied")

        state = request.query_params.get("state", "")
        code = request.query_params.get("code", "")
        state_payload = self._read_state(request)
        if (
            state_payload is None
            or not state
            or not secrets.compare_digest(state, state_payload["nonce"])
            or not code
        ):
            return self._callback_redirect("/error?reason=expired")

        try:
            token_payload = await self._exchange_code(code)
            access_token = _required_string(token_payload, "access_token")
            profile = await self._fetch_profile(access_token)
            expires_in = _positive_int(token_payload.get("expires_in"), default=3600)

            if state_payload["intent"] == "login":
                await self._authorization_service.record_user(profile)
                response = self._callback_redirect("/servers")
                self._set_session_cookie(
                    response,
                    access_token=access_token,
                    profile=profile,
                    expires_in=expires_in,
                )
                return response

            if state_payload["intent"] != "install":
                return self._callback_redirect("/error?reason=expired")

            existing_session = self._read_session(request)
            if (
                existing_session is None
                or existing_session["discord_user_id"] != profile["discord_user_id"]
                or state_payload["user_id"] != profile["discord_user_id"]
            ):
                return self._callback_redirect("/error?reason=expired")

            guild_id = state_payload["guild_id"]
            guild = await self._authorization_service.bootstrap_onboarding_guild(
                guild_id=guild_id,
                access_token=access_token,
                profile=profile,
            )
        except (
            DiscordApiError,
            DiscordPermissionError,
            httpx.HTTPError,
            ValueError,
        ):
            return self._callback_redirect("/error?reason=install")

        response = self._success_redirect(guild.name, callback=True)
        self._set_session_cookie(
            response,
            access_token=access_token,
            profile=profile,
            expires_in=expires_in,
        )
        return response

    async def list_guilds(self, request: Request) -> Response:
        """Return visible guilds and their onboarding status for the signed-in user."""

        session = self._read_session(request)
        if session is None:
            return self._json(
                {"status": "authentication_required", "login_url": "/onboarding/start"},
                status_code=401,
            )
        try:
            guilds = await self._authorization_service.list_onboarding_guilds(
                access_token=session["access_token"],
                discord_user_id=session["discord_user_id"],
            )
        except (DiscordApiError, DiscordPermissionError, httpx.HTTPError) as error:
            return self._json(
                {"status": "error", "message": str(error)},
                status_code=502,
            )

        return self._json(
            {
                "status": "ok",
                "user": {
                    "id": session["discord_user_id"],
                    "username": session["username"],
                    "display_name": session["display_name"],
                    "avatar_url": session["avatar_url"],
                },
                "csrf_token": session["csrf_token"],
                "guilds": [asdict(guild) for guild in guilds],
            }
        )

    async def activate_guild(self, request: Request) -> Response:
        """Persist access for an administrator after live bot verification."""

        session = self._read_session(request)
        if session is None:
            return self._json({"status": "authentication_required"}, status_code=401)
        supplied_csrf = request.headers.get("X-GuildSpan-CSRF", "")
        if not supplied_csrf or not secrets.compare_digest(
            supplied_csrf,
            session["csrf_token"],
        ):
            return self._json({"status": "invalid_request"}, status_code=403)

        guild_id = request.path_params.get("guild_id", "")
        if not isinstance(guild_id, str) or not _valid_snowflake(guild_id):
            return self._json({"status": "invalid_guild"}, status_code=400)

        profile: DiscordProfile = {
            "discord_user_id": session["discord_user_id"],
            "username": session["username"],
            "display_name": session["display_name"],
            "avatar_url": session["avatar_url"],
        }
        try:
            guild = await self._authorization_service.bootstrap_onboarding_guild(
                guild_id=guild_id,
                access_token=session["access_token"],
                profile=profile,
            )
        except DiscordPermissionError as error:
            return self._json(
                {"status": "not_allowed", "message": str(error)},
                status_code=403,
            )
        except (DiscordApiError, httpx.HTTPError) as error:
            return self._json(
                {"status": "bot_unavailable", "message": str(error)},
                status_code=409,
            )

        query = urlencode({"source": "onboarding", "guild": guild.name})
        return self._json({"status": "ok", "redirect": f"/success?{query}"})

    def _authorization_redirect(
        self,
        *,
        intent: str,
        guild_id: str = "",
        user_id: str = "",
        install_bot: bool = False,
    ) -> Response:
        nonce = secrets.token_urlsafe(32)
        state_payload: _StatePayload = {
            "nonce": nonce,
            "intent": intent,
            "guild_id": guild_id,
            "user_id": user_id,
            "expires_at": int(time.time()) + ONBOARDING_STATE_TTL_SECONDS,
        }
        scopes = ["identify", "guilds"]
        parameters: dict[str, str] = {
            "response_type": "code",
            "client_id": self._auth_settings.discord_client_id,
            "redirect_uri": self._callback_url,
            "scope": " ".join(scopes),
            "state": nonce,
        }
        if install_bot:
            scopes.append("bot")
            parameters.update(
                scope=" ".join(scopes),
                permissions=str(self._settings.discord_bot_permissions),
                guild_id=guild_id,
                disable_guild_select="true",
                integration_type="0",
                prompt="consent",
            )

        response = RedirectResponse(
            f"{DISCORD_AUTHORIZE_URL}?{urlencode(parameters)}",
            status_code=302,
        )
        response.set_cookie(
            ONBOARDING_STATE_COOKIE,
            self._seal(cast(dict[str, object], state_payload)),
            max_age=ONBOARDING_STATE_TTL_SECONDS,
            path="/onboarding",
            secure=self._secure_cookies,
            httponly=True,
            samesite="lax",
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    async def _exchange_code(self, code: str) -> dict[str, object]:
        response = await self._http_client.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": self._auth_settings.discord_client_id,
                "client_secret": self._auth_settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self._callback_url,
            },
            headers={"Accept": "application/json"},
        )
        if not response.is_success:
            raise DiscordApiError(
                f"Discord OAuth token exchange failed with status {response.status_code}."
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise DiscordApiError("Discord returned an invalid OAuth token response.")
        return cast(dict[str, object], payload)

    async def _fetch_profile(self, access_token: str) -> DiscordProfile:
        response = await self._http_client.get(
            DISCORD_CURRENT_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if not response.is_success:
            raise DiscordApiError(
                f"Discord user lookup failed with status {response.status_code}."
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise DiscordApiError("Discord returned an invalid user profile.")
        user = cast(dict[str, object], payload)
        discord_user_id = _required_string(user, "id")
        username = _optional_string(user.get("username"))
        display_name = _optional_string(user.get("global_name")) or username
        avatar_hash = _optional_string(user.get("avatar"))
        avatar_url = (
            f"https://cdn.discordapp.com/avatars/{discord_user_id}/"
            f"{avatar_hash}.png?size=256"
            if avatar_hash
            else None
        )
        return {
            "discord_user_id": discord_user_id,
            "username": username,
            "display_name": display_name,
            "avatar_url": avatar_url,
        }

    @property
    def _callback_url(self) -> str:
        return f"{self._auth_settings.public_base_url}{ONBOARDING_CALLBACK_PATH}"

    def _set_session_cookie(
        self,
        response: Response,
        *,
        access_token: str,
        profile: DiscordProfile,
        expires_in: int,
    ) -> None:
        max_age = min(expires_in, ONBOARDING_SESSION_TTL_SECONDS)
        session_payload: _SessionPayload = {
            "access_token": access_token,
            "discord_user_id": profile["discord_user_id"],
            "username": profile["username"],
            "display_name": profile["display_name"],
            "avatar_url": profile["avatar_url"],
            "csrf_token": secrets.token_urlsafe(32),
            "expires_at": int(time.time()) + max_age,
        }
        response.set_cookie(
            ONBOARDING_SESSION_COOKIE,
            self._seal(cast(dict[str, object], session_payload)),
            max_age=max_age,
            path="/",
            secure=self._secure_cookies,
            httponly=True,
            samesite="lax",
        )

    def _read_state(self, request: Request) -> _StatePayload | None:
        payload = self._open(request.cookies.get(ONBOARDING_STATE_COOKIE))
        if payload is None or not _not_expired(payload):
            return None
        required = ("nonce", "intent", "guild_id", "user_id")
        if not all(isinstance(payload.get(key), str) for key in required):
            return None
        return cast(_StatePayload, payload)

    def _read_session(self, request: Request) -> _SessionPayload | None:
        payload = self._open(request.cookies.get(ONBOARDING_SESSION_COOKIE))
        if payload is None or not _not_expired(payload):
            return None
        if not isinstance(payload.get("access_token"), str):
            return None
        if not isinstance(payload.get("discord_user_id"), str):
            return None
        if not isinstance(payload.get("csrf_token"), str):
            return None
        return cast(_SessionPayload, payload)

    def _seal(self, payload: dict[str, object]) -> str:
        serialized = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return self._fernet.encrypt(serialized).decode("ascii")

    def _open(self, value: str | None) -> dict[str, object] | None:
        if not value:
            return None
        try:
            payload = json.loads(self._fernet.decrypt(value.encode("ascii")))
        except (InvalidToken, UnicodeError, ValueError, json.JSONDecodeError):
            return None
        return cast(dict[str, object], payload) if isinstance(payload, dict) else None

    def _callback_redirect(self, path: str) -> Response:
        response = self._local_redirect(path)
        response.delete_cookie(
            ONBOARDING_STATE_COOKIE,
            path="/onboarding",
            secure=self._secure_cookies,
            httponly=True,
            samesite="lax",
        )
        return response

    def _success_redirect(self, guild_name: str, *, callback: bool = False) -> Response:
        query = urlencode({"source": "onboarding", "guild": guild_name})
        path = f"/success?{query}"
        return self._callback_redirect(path) if callback else self._local_redirect(path)

    @staticmethod
    def _local_redirect(path: str) -> Response:
        response = RedirectResponse(path, status_code=303)
        response.headers["Cache-Control"] = "no-store"
        return response

    @staticmethod
    def _json(payload: dict[str, object], *, status_code: int = 200) -> Response:
        response = JSONResponse(payload, status_code=status_code)
        response.headers["Cache-Control"] = "no-store"
        return response


def _valid_snowflake(value: str) -> bool:
    return value.isascii() and value.isdigit() and 5 <= len(value) <= 20


def _required_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, (str, int)) or not str(value).strip():
        raise ValueError(f"Discord response is missing {key}.")
    return str(value)


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _positive_int(value: object, *, default: int) -> int:
    try:
        parsed = int(cast(str | int, value))
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _not_expired(payload: dict[str, object]) -> bool:
    expires_at = payload.get("expires_at")
    return isinstance(expires_at, int) and expires_at >= int(time.time())
