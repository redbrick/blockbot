import datetime
import logging
import typing
from urllib.parse import urlparse

import aiohttp
import arc
import hikari

from src.config import (
    ADMIN_API_PASSWORD,
    ADMIN_API_USERNAME,
    LDAP_PASSWORD,
    LDAP_USERNAME,
)

logger = logging.getLogger(__name__)


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


async def get_ldap_user_by_discord_id(
    discord_id: int, aiohttp_client: aiohttp.ClientSession
) -> dict[str, typing.Any] | None:
    """
    Get the LDAP user associated with a Discord ID.
    Returns None if no user is found.
    """
    url = f"https://api.redbrick.dcu.ie/admin/users/discord/{discord_id}"
    auth = aiohttp.BasicAuth(login=ADMIN_API_USERNAME or "", password=ADMIN_API_PASSWORD or "")
    async with aiohttp_client.get(url, auth=auth) as response:
        logger.error(f"Fetching LDAP user for Discord ID: {discord_id}")
        if response.status == 404:
            return None
        response.raise_for_status()
        return await response.json()


async def get_ldap_user_by_uid(
    uid: str, aiohttp_client: aiohttp.ClientSession
) -> dict[str, typing.Any] | None:
    """
    Get the LDAP user associated with a UID.
    Returns None if no user is found.
    """
    url = f"https://api.redbrick.dcu.ie/admin/users/{uid}"
    auth = aiohttp.BasicAuth(login=ADMIN_API_USERNAME or "", password=ADMIN_API_PASSWORD or "")
    async with aiohttp_client.get(url, auth=auth) as response:
        logger.error(f"Fetching LDAP user for UID: {uid}")
        if response.status == 404:
            return None
        response.raise_for_status()
        return await response.json()


async def is_uid_ldap_available(
    aiohttp_client: aiohttp.ClientSession, uid: str
) -> bool:
    """
    Check if LDAP user exists with that username.
    """
    url = f"https://api.redbrick.dcu.ie/users/{uid}"
    async with aiohttp_client.get(url) as response:
        if response.status == 404:
            return True
        if response.status == 200:
            return False
        response.raise_for_status()
        return False


async def link_discord_to_ldap(
    discord_id: int, uid: str, aiohttp_client: aiohttp.ClientSession
) -> bool:
    """
    Link a Discord ID to an LDAP user.
    """
    url = f"https://api.redbrick.dcu.ie/admin/users/{uid}"
    auth = aiohttp.BasicAuth(login=ADMIN_API_USERNAME or "", password=ADMIN_API_PASSWORD or "")
    data = {"ldap_key": "discord", "ldap_value": discord_id}
    async with aiohttp_client.put(url, data=data, auth=auth) as response:
        if response.status != 200:
            logger.error(
                f"Failed to link Discord ID {discord_id} to LDAP user {uid}. Status code: {response.status}"
            )
            return False
        response.raise_for_status()
        return True
