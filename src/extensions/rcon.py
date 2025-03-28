import arc
from rcon.exceptions import (  # pyright: ignore[reportMissingTypeStubs]
    SessionTimeout,
    WrongPassword,
)
from rcon.source import rcon  # pyright: ignore[reportMissingTypeStubs]

from src.config import (
    CHANNEL_IDS,
    RCON_HOST,
    RCON_PASSWORD,
    RCON_PORT,
    ROLE_IDS,
    Feature,
)
from src.hooks import restrict_to_channels, restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Minecraft RCON Plugin", required_features=[Feature.RCON])

whitelist = plugin.include_slash_group("whitelist", "Manage Minecraft whitelist.")


@whitelist.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["admins"]]))
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_subcommand("add", "Whitelist a Minecraft player.")
async def whitelist_add(
    ctx: BlockbotContext,
    username: arc.Option[str, arc.StrParams("Minecraft username to whitelist")],
) -> None:
    response = await run_rcon_command("add", username)
    await ctx.respond(f"`{username}`: {response}")


@whitelist.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["admins"]]))
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_subcommand("remove", "Remove a Minecraft player from the whitelist.")
async def whitelist_remove(
    ctx: BlockbotContext,
    username: arc.Option[
        str, arc.StrParams("Minecraft username to remove from whitelist")
    ],
) -> None:
    response = await run_rcon_command("remove", username)
    await ctx.respond(f"`{username}`: {response}")


async def run_rcon_command(command: str, username: str) -> str:
    assert RCON_HOST is not None and RCON_PORT is not None and RCON_PASSWORD is not None

    return await rcon(
        "whitelist",
        command,
        username,
        host=RCON_HOST,
        port=RCON_PORT,
        passwd=RCON_PASSWORD,
    )


@whitelist.set_error_handler
async def rcon_error_handler(ctx: BlockbotContext, exc: Exception) -> None:
    if isinstance(exc, WrongPassword):
        await ctx.respond(
            "❌ Incorrect RCON password.",
        )
        return
    if isinstance(exc, SessionTimeout):
        await ctx.respond("❌ Session Timeout.")
        return

    raise exc


@arc.loader
def load(client: Blockbot) -> None:
    client.add_plugin(plugin)
