import hikari
from arc import GatewayClient

async def get_guild(client: GatewayClient, event: hikari.GuildMessageCreateEvent):
    return event.get_guild() or await client.rest.fetch_guild(event.guild_id)

def role_mention(role: hikari.Snowflake | str): return f"<@&{role}>"
