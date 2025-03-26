import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="gerry")

image = "https://cdn.redbrick.dcu.ie/blockbot/gerry.jpg"


@plugin.include
@arc.slash_command("gerry", "So tell me Frank!")
async def gerry_command(
    ctx: BlockbotContext,
    user: arc.Option[
        hikari.User | None,
        arc.UserParams("The user to send a gerry to."),
    ] = None,
) -> None:
    """Send a gerry!"""
    if user is not None:
        description = f"So tell me {user.mention}!"
    else:
        description = "So tell me Frank!"

    embed = hikari.Embed(
        title="Gerry",
        description=description,
        colour=Colour.GERRY_YELLOW,
    )
    embed = embed.set_image(image)

    await ctx.respond(embed)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
