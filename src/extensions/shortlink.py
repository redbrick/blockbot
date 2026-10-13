from typing import cast
from urllib.parse import urlsplit

import aiohttp
import arc
import hikari

from src.config import ROLE_IDS, SHLINK_API_KEY, SHLINK_API_URL, Feature
from src.hooks import restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Shlink", required_features=[Feature.SHLINK])


class ShlinkAPIError(Exception):
    """Raised when Shlink returns a non-success response."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"Shlink returned HTTP {status}")


def validate_long_url(value: str) -> str:
    """Return a valid HTTP(S) URL or raise ValueError."""
    url = value.strip()
    parsed = urlsplit(url)

    if (
        len(url) > 2048
        or any(character.isspace() for character in url)
        or parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            "Please provide a valid HTTP or HTTPS URL (up to 2048 characters)."
        )

    return url


async def create_short_url(
    url: str,
    session: aiohttp.ClientSession,
    *,
    api_url: str,
    api_key: str,
) -> str:
    """Create a Shlink short URL and return its public URL."""
    async with session.post(
        api_url,
        json={"longUrl": url},
        headers={"X-Api-Key": api_key, "Accept": "application/json"},
        allow_redirects=False,
    ) as response:
        if response.status < 200 or response.status >= 300:
            raise ShlinkAPIError(response.status)

        payload = await response.json()

    if not isinstance(payload, dict):
        raise ValueError("Shlink returned an invalid response.")

    short_url = cast("dict[str, object]", payload).get("shortUrl")
    if not isinstance(short_url, str):
        raise ValueError("Shlink did not return a short URL.")

    parsed = urlsplit(short_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Shlink returned an invalid short URL.")

    return short_url


@plugin.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["brickie"]]))
@arc.slash_command(
    "shortlink",
    "Create a short link with Shlink.",
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def shortlink(
    ctx: BlockbotContext,
    url: arc.Option[str, arc.StrParams("The URL to shorten.")],
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Create a Shlink short URL for Redbrick members."""
    try:
        long_url = validate_long_url(url)
    except ValueError as error:
        await ctx.respond(f"❌ {error}", flags=hikari.MessageFlag.EPHEMERAL)
        return

    assert SHLINK_API_KEY is not None and SHLINK_API_URL is not None

    try:
        short_url = await create_short_url(
            long_url,
            aiohttp_client,
            api_url=SHLINK_API_URL,
            api_key=SHLINK_API_KEY,
        )
    except ShlinkAPIError as error:
        await ctx.respond(
            f"❌ Shlink could not create the shortlink (HTTP `{error.status}`).",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    except aiohttp.ClientError, TimeoutError:
        await ctx.respond(
            "❌ Could not connect to Shlink. Please try again later.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    except ValueError:
        await ctx.respond(
            "❌ Shlink returned an invalid response.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await ctx.respond(f"✅ {short_url}", flags=hikari.MessageFlag.EPHEMERAL)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
