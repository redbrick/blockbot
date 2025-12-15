import collections
import itertools

import arc
import hikari

from src.config import Colour
from src.hooks import RoleRestrictedHook
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Help Command Plugin")


def gather_commands(ctx: BlockbotContext) -> dict[str | None, list[str]]:
    """Gathers commands grouped by their plugin, filtered by user roles."""
    plugin_commands: dict[str | None, list[str]] = collections.defaultdict(list)

    for plugin_, commands in itertools.groupby(
        plugin.client.walk_commands(hikari.CommandType.SLASH),
        key=lambda cmd: cmd.plugin,
    ):
        for cmd in commands:
            if not isinstance(cmd, (arc.SlashCommand, arc.SlashSubCommand)):
                continue

            # Check if the command has hooks
            hooks = cmd.hooks

            required_roles: set[int] = set()
            for hook in hooks:
                if isinstance(hook, RoleRestrictedHook):
                    required_roles.update(hook.role_ids)

            if not ctx.member or (
                required_roles
                and not any(
                    role_id in ctx.member.role_ids for role_id in required_roles
                )
            ):
                continue

            # Add the command to the plugin_commands dictionary
            plugin_commands[plugin_.name if plugin_ else None].append(
                f"{cmd.make_mention()} - {cmd.description}"
            )

    return plugin_commands


@plugin.include
@arc.slash_command("help", "Displays a list of all commands.")
async def help_command(ctx: BlockbotContext) -> None:
    """Displays a simple list of all bot commands."""

    # Gather commands filtered by user roles
    plugin_commands = gather_commands(ctx)

    # Build the embed fields directly from the plugin_commands dictionary
    embed = hikari.Embed(title="Bot Commands", color=Colour.HELP_GREEN)
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
