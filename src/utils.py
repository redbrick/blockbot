import datetime
import typing
from urllib.parse import urlparse

import aiohttp
import arc
import hikari

from src.config import LDAP_PASSWORD, LDAP_USERNAME


class EventWithGuildAttributes(typing.Protocol):
    @property
    def guild_id(self) -> hikari.Snowflake: ...

    def get_guild(self) -> hikari.GatewayGuild | None: ...


async def get_guild(
    client: arc.GatewayClient,
    event: EventWithGuildAttributes,
) -> hikari.GatewayGuild | hikari.RESTGuild:
    return event.get_guild() or await client.rest.fetch_guild(event.guild_id)


def role_mention(role_id: hikari.Snowflake | int | str) -> str:
    return f"<@&{role_id}>"


def channel_mention(channel_id: hikari.Snowflake | int | str) -> str:
    return f"<#{channel_id}>"


async def hedgedoc_login(aiohttp_client: aiohttp.ClientSession) -> None:
    data = {
        "username": LDAP_USERNAME,
        "password": LDAP_PASSWORD,
    }

    await aiohttp_client.post("https://md.redbrick.dcu.ie/auth/ldap", data=data)


async def get_md_content(url: str, aiohttp_client: aiohttp.ClientSession) -> str:
    """
    Get the content of a note at a HedgeDoc URL.
    """
    if "https://md.redbrick.dcu.ie" not in url:
        raise ValueError(f"`{url}` is not a valid MD URL. Please provide a valid URL.")

    await hedgedoc_login(aiohttp_client)

    parsed_url = urlparse(url)
    request_url = (
        f"{parsed_url.scheme}://{parsed_url.hostname}{parsed_url.path}/download"
    )

    async with aiohttp_client.get(request_url) as response:
        response.raise_for_status()
        return await response.text()


async def post_new_md_content(
    content: str, aiohttp_client: aiohttp.ClientSession
) -> str:
    post_url = "https://md.redbrick.dcu.ie/new"
    post_headers = {"Content-Type": "text/markdown"}

    async with aiohttp_client.post(
        url=post_url,
        headers=post_headers,
        data=content,
    ) as response:
        response.raise_for_status()

    return str(response.url)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)
