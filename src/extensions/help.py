import hikari
import arc
import itertools

plugin = arc.GatewayPlugin(name="Help Command Plugin")


def gather_commands(client: arc.GatewayClient):
    command_list = []
    for command in itertools.chain(client.walk_commands(hikari.CommandType.SLASH)):
        command_list.append(
            {
                "name": command.name,
                "description": command.description or "No description provided.",
            }
        )
    return command_list


@plugin.include
@arc.slash_command("help", "Displays a list of all commands.")
async def help_command(ctx: arc.GatewayContext) -> None:
    """Displays a simple list of all bot commands."""

    commands = gather_commands(ctx.client)
    embed = hikari.Embed(title="Bot Commands", color=0x00FF00)

    for command in commands:
        embed.add_field(
            name=f"/{command['name']}", value=command["description"], inline=False
        )

    await ctx.respond(embed=embed)


@arc.loader
def load(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
