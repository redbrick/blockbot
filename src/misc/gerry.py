import arc
import hikari

from src.config import Colour
from src.models import BlockbotContext, BlockbotPlugin, command_loader

IMAGE = "https://cdn.redbrick.dcu.ie/blockbot/gerry.jpg"
GERRY_VIDEO_URL = "https://www.youtube.com/watch?v=RdiUq3eoSNc"

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
        url=GERRY_VIDEO_URL,
        colour=Colour.GERRY_YELLOW,
    )
    embed = embed.set_image(IMAGE)

    await ctx.respond(embed)


@command_loader
def loader(plugin: BlockbotPlugin) -> None:
    plugin.add_command(gerry_command)
