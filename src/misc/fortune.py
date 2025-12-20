import arc
import hikari
from fortune import fortune  # pyright: ignore[reportMissingTypeStubs]

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="fortune")


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


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
