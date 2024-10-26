import arc
import hikari


from pyfiglet import Figlet

plugin = arc.GatewayPlugin(name="figlet")

style_choices = [
    hikari.CommandChoice(name="Default", value="standard"),
    hikari.CommandChoice(name="Slant", value="slant"),
    hikari.CommandChoice(name="weird", value="stanpatello"),
    hikari.CommandChoice(name="USA", value="usaflag"),
    hikari.CommandChoice(name="CyberMedium", value="cybermedium"),
    hikari.CommandChoice(name="wideterm", value="wideterm"),
    hikari.CommandChoice(name="Lean", value="lean"),
    hikari.CommandChoice(name="3-D", value="3-d"),
    hikari.CommandChoice(name="larry3d", value="larry3d"),
    hikari.CommandChoice(name="Letters", value="letters"),
    hikari.CommandChoice(name="Poison", value="poison"),
    hikari.CommandChoice(name="doh", value="doh"),
    hikari.CommandChoice(name="epic", value="epic"),
    hikari.CommandChoice(name="fraktur", value="fraktur"),
    hikari.CommandChoice(name="graffiti", value="graffiti"),
    hikari.CommandChoice(name="katakana", value="katakana"),
]


@plugin.include
@arc.slash_command("figlet", "ASCIIify your words!")
async def figlet_command(
    ctx: arc.GatewayContext,
    text: arc.Option[str, arc.StrParams("Your words to ASCIIify.")],
    style: arc.Option[
        str,
        arc.StrParams("The style of your ASCII text", choices=style_choices),
    ] = "standard",
) -> None:
    """ASCIIify words"""

    figlet = Figlet(font=style)

    try:
        # generate ASCII art
        ascii_art = figlet.renderText(text)
    except Exception as e:
        await ctx.respond(f"Failed to generate ASCII art: {e}")
        return

    # do not exceed Discord's 2000 character limit
    if len(ascii_art) > 2000:
        await ctx.respond(
            "The generated ASCII art is too long to send. Please try a shorter text."
        )
    else:
        # send ASCII art in a codeblock
        await ctx.respond(f"```\n{ascii_art}\n```")


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
