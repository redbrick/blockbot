import datetime

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


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)
