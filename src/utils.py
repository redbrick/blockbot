import hikari
from arc import GatewayClient


async def get_guild(
    client: GatewayClient, event: hikari.GuildMessageCreateEvent
) -> hikari.GatewayGuild | hikari.RESTGuild:
    return event.get_guild() or await client.rest.fetch_guild(event.guild_id)


def role_mention(role_id: hikari.Snowflake | int | str) -> str:
    return f"<@&{role_id}>"
