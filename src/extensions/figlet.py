import arc
import hikari

from pyfiglet import Figlet

plugin = arc.GatewayPlugin(name="figlet")

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
    ctx: arc.GatewayContext,
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
    ascii_art = figlet.renderText(text)
    assert len(ascii_art) > 0

    # wrap ASCII art in a codeblock
    message = f"```{ascii_art}```"

    # do not exceed Discord's 2000 character limit
    if len(message) > 2000:
        await ctx.respond(
            "The generated ASCII art is too long to send. Please try a shorter text.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    else:
        # send ASCII art in a codeblock
        await ctx.respond(message)


@plugin.set_error_handler
async def figlet_error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    text = ctx.get_option("text", arc.OptionType.STRING)
    assert text is not None

    if isinstance(exc, AssertionError):
        await ctx.respond(
            f"❌ Failed to generate ASCII art for: {text}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    raise exc


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
