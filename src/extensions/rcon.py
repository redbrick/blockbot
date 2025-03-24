import os
import arc
import hikari
from rcon.source import rcon

from src.config import RCON_HOST, RCON_PASSWORD, RCON_PORT, CHANNEL_IDS, ROLE_IDS
from src.hooks import restrict_to_channels, restrict_to_roles

plugin = arc.GatewayPlugin(name="Minecraft RCON Plugin")

@plugin.include
@arc.with_hook(
    restrict_to_roles(role_ids=[ROLE_IDS["admins"]]),
)
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_command(
    "whitelist",
    "Whitelist a Minecraft player",
)
async def whitelist_command(
    ctx: arc.GatewayContext,
    username: arc.Option[
        str, 
        arc.StrParams(
            description="Minecraft username to whitelist"
        )
    ]
) -> None:
    if not RCON_HOST or not RCON_PASSWORD:
        await ctx.respond("RCON configuration is missing. Please check your environment variables.")
        return

    try:
        # rcon docs: https://rcon.readthedocs.io/en/latest/
        response = await rcon(
            "whitelist", "add", username,
            host=RCON_HOST,
            port=int(RCON_PORT),
            passwd=RCON_PASSWORD
        )
        await ctx.respond(f"`{username}`: {response}")
    except Exception as e:
        await ctx.respond(f"Error whitelisting `{username}`: {str(e)}")

@arc.loader
def load(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
