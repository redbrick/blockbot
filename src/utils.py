import datetime
from urllib.parse import urlparse

import aiohttp
import hikari
from arc import GatewayClient

from src.config import LDAP_PASSWORD, LDAP_USERNAME


async def get_guild(
    client: GatewayClient,
    event: hikari.GuildMessageCreateEvent,
) -> hikari.GatewayGuild | hikari.RESTGuild:
    return event.get_guild() or await client.rest.fetch_guild(event.guild_id)


def role_mention(role_id: hikari.Snowflake | int | str) -> str:
    return f"<@&{role_id}>"


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
