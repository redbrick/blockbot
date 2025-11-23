import collections
import itertools

import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Help Command Plugin")


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
async def help_command(ctx: BlockbotContext) -> None:
    """Displays a simple list of all bot commands."""

    embed = hikari.Embed(title="Bot Commands", color=Colour.HELP_GREEN)
    plugin_commands = collections.defaultdict(list)

    # Iterate over all commands and group them by plugin
    for plugin_, commands in itertools.groupby(
        plugin.client.walk_commands(hikari.CommandType.SLASH),
        key=lambda cmd: cmd.plugin,
    ):
        for cmd in commands:
            if not isinstance(cmd, (arc.SlashCommand, arc.SlashSubCommand)):
                continue

            # Check if the command has hooks
            hooks = getattr(cmd, "hooks", None)
            required_roles = None

            if hooks:
                # Use getattr to directly fetch role_ids from the first hook that has it
                required_roles = next(
                    (getattr(hook, "role_ids", None) for hook in hooks if getattr(hook, "role_ids", None)),
                    None,
                )

            # Check roles of member
            if required_roles and not any(role_id in ctx.member.role_ids for role_id in required_roles):
                continue

            # Add the command to the plugin_commands dictionary
            plugin_commands[plugin_.name if plugin_ else None].append(
                f"{cmd.make_mention()} - {cmd.description}"
            )

    # Build the embed fields directly from the plugin_commands dictionary
    for plugin_name, commands in plugin_commands.items():
        embed.add_field(
            name=plugin_name or "No plugin",
            value="\n".join(commands),
            inline=False,
        )

    await ctx.respond(embed=embed)


@arc.loader
def load(client: Blockbot) -> None:
    client.add_plugin(plugin)
