import collections
import itertools

import arc
import hikari

from src.config import Colour

plugin = arc.GatewayPlugin(name="Help Command Plugin")


def gather_commands() -> dict[str | None, list[str]]:
    plugin_commands: dict[str | None, list[str]] = collections.defaultdict(list)

    for plugin_, commands in itertools.groupby(
        plugin.client.walk_commands(hikari.CommandType.SLASH),
        key=lambda cmd: cmd.plugin,
    ):
        for cmd in commands:
            if not isinstance(cmd, (arc.SlashCommand, arc.SlashSubCommand)):
                continue

            plugin_commands[plugin_.name if plugin_ else None].append(
                f"{cmd.make_mention()} - {cmd.description}",
            )

    return plugin_commands


@plugin.include
@arc.slash_command("help", "Displays a list of all commands.")
async def help_command(ctx: arc.GatewayContext) -> None:
    """Displays a simple list of all bot commands."""

    plugin_commands = gather_commands()
    embed = hikari.Embed(title="Bot Commands", color=Colour.HELP_GREEN)

    for plugin_, commands in plugin_commands.items():
        embed.add_field(
            name=plugin_ or "No plugin",
            value="\n".join(commands),
            inline=False,
        )

    await ctx.respond(embed=embed)


@arc.loader
def load(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
