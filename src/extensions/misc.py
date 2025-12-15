import arc
import hikari
from fortune import fortune  # pyright: ignore[reportMissingTypeStubs]
from pyfiglet import Figlet  # pyright: ignore[reportMissingTypeStubs]

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="misc")

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


@plugin.include
@arc.slash_command("fortune", "Send a user a random Fortune!")
async def fortune_command(
    ctx: BlockbotContext,
    user: arc.Option[hikari.User | None, arc.UserParams("A user")] = None,
) -> None:
    """Send a random Fortune!"""

    # generate fortune
    fortune_message = fortune()  # pyright: ignore[reportUnknownVariableType]
    if not fortune_message:
        await ctx.respond(
            "❌ Failed to generate fortune. Please try again.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # mention user if present
    if user is not None:
        message = f"Dear {user.mention},\n```{fortune_message}```"
    else:
        message = f"```{fortune_message}```"

        # do not exceed Discord's 2000 character limit
    if len(message) > 2000:
        await ctx.respond(
            "❌ FThe generated fortune is too long to send. Please try again.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # send fortune in a codeblock
    await ctx.respond(message, user_mentions=True)


fonts = [
    "standard",
    "slant",
    "stanpatello",
    "usaflag",
    "cybermedium",
    "wideterm",
    "lean",
    "3-d",
    "larry3d",
    "letters",
    "poison",
    "doh",
    "epic",
    "fraktur",
    "graffiti",
    "katakana",
]


@plugin.include
@arc.slash_command("figlet", "ASCIIify your words!")
async def figlet_command(
    ctx: BlockbotContext,
    text: arc.Option[str, arc.StrParams("Your words to ASCIIify.")],
    font: arc.Option[
        str,
        arc.StrParams(
            "The style of your ASCII text",
            choices=[
                hikari.CommandChoice(name=font.capitalize(), value=font)
                for font in fonts
            ],
        ),
    ] = "standard",
) -> None:
    """ASCIIify words"""

    # create Figlet object with the selected font
    figlet = Figlet(font=font)

    # generate ASCII art
    ascii_art = figlet.renderText(text)  # pyright: ignore[reportUnknownMemberType]
    if not ascii_art:
        await ctx.respond(
            "❌ Failed to generate ASCII art. Please try again.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # wrap ASCII art in a codeblock
    message = f"```{ascii_art}```"

    # do not exceed Discord's 2000 character limit
    if len(message) > 2000:
        await ctx.respond(
            "❌ The generated ASCII art is too long to send. Please try a shorter text.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # send ASCII art in a codeblock
    await ctx.respond(message)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
