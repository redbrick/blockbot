import arc

from rcon.source import rcon

from src.config import RCON_HOST, RCON_PASSWORD, RCON_PORT, CHANNEL_IDS, ROLE_IDS
from src.hooks import restrict_to_channels, restrict_to_roles

plugin = arc.GatewayPlugin(name="Minecraft RCON Plugin")

whitelist = plugin.include_slash_group("whitelist", "Manage Minecraft whitelist.")

@whitelist.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["admins"]]))
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_subcommand("add", "Whitelist a Minecraft player.")
async def whitelist_add(
    ctx: arc.GatewayContext,
    username: arc.Option[str, arc.StrParams("Minecraft username to whitelist")]
) -> None:
    if not RCON_HOST or not RCON_PASSWORD or not RCON_PORT:
        await ctx.respond(
            "RCON configuration is missing. Please check your environment variables.",
        )
        return

    try:
        # rcon docs: https://rcon.readthedocs.io/en/latest/
        response = await rcon(
            "whitelist", "add", username,
            host=RCON_HOST,
            port=int(RCON_PORT),
            passwd=RCON_PASSWORD
        )
        await ctx.respond(
            f"`{username}`: {response}",
        )
    except Exception as e:
        await ctx.respond(
            f"Error whitelisting `{username}`: {str(e)}",
        )


@whitelist.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["admins"]]))
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_subcommand("remove", "Remove a Minecraft player from the whitelist.")
async def whitelist_remove(
    ctx: arc.GatewayContext,
    username: arc.Option[str, arc.StrParams("Minecraft username to remove from whitelist")]
) -> None:
    if not RCON_HOST or not RCON_PASSWORD or not RCON_PORT:
        await ctx.respond(
            "RCON configuration is missing. Please check your environment variables.",
        )
        return

    try:
        response = await rcon(
            "whitelist", "remove", username,
            host=RCON_HOST,
            port=int(RCON_PORT),
            passwd=RCON_PASSWORD
        )
        await ctx.respond(
            f"`{username}`: {response}",
        )
    except Exception as e:
        await ctx.respond(
            f"Error removing `{username}`: {str(e)}",
        )

@arc.loader
def load(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
