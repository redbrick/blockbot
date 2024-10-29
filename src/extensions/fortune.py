import arc
import hikari
from fortune import fortune

fortune_cmd = arc.GatewayPlugin(name="fortune")


@fortune_cmd.include
@arc.slash_command("fortune", "Send a user a random Fortune!")
async def fortune_command(
    ctx: arc.GatewayContext,
    user: arc.Option[hikari.User, arc.UserParams("A user")] = None,
) -> None:
    """Send a user a random Fortune!"""

    # generate fortune
    fortune_message = fortune()
    assert len(fortune_message) > 0

    if user is not None:
        message = f"Dear {user.mention},\n```{fortune_message}```"
    else:
        message = f"```{fortune_message}```"

        # do not exceed Discord's 2000 character limit
    if len(message) > 2000:
        await ctx.respond(
            "The generated fortune is too long to send. Please try again.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    # send fortune in a codeblock
    await ctx.respond(message)


@fortune_cmd.set_error_handler
async def fortune_error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    user = ctx.get_option("user", arc.OptionType.USER)
    assert user is not None

    if isinstance(exc, AssertionError):
        await ctx.respond(
            "❌ Failed to generate the fortune. Please try again.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    if isinstance(exc, hikari.NotFoundError):
        await ctx.respond(
            "❌ Blockbot can't find that user.", flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    raise exc


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(fortune_cmd)
