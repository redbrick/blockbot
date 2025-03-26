import arc

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Example Commands")


@plugin.include
@arc.slash_command("hello", "Say hello!")
async def hello(ctx: BlockbotContext) -> None:
    """An individual command, invoked by `/hello`."""
    await ctx.respond("Hello from hikari and hikari-arc!")


group = plugin.include_slash_group(
    "base_group",
    "A base command group, with sub groups and sub commands.",
)


@group.include
@arc.slash_subcommand("sub_command", "A sub command")
async def sub_command(ctx: BlockbotContext) -> None:
    """A subcommand, invoked by `/base_command sub_command`."""
    await ctx.respond("Hello, world! This is a sub command")


sub_group = group.include_subgroup("sub_group", "A subgroup to add commands to.")


@sub_group.include
@arc.slash_subcommand("sub_command", "A subgroup subcommand.")
async def sub_group_sub_command(ctx: BlockbotContext) -> None:
    """A subcommand belonging to a subgroup, invoked by `/base_group sub_group sub_command`."""
    await ctx.respond("This is a subgroup subcommand.")


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
