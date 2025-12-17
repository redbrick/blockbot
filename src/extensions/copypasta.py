import os

import aiofiles
import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Copypasta")

MAX_EMBED = 4096
MAX_MESSAGE = 6000


async def load_text(file_name: str) -> list[list[str]]:
    async with aiofiles.open(
        f"./src/copypastas/{file_name}.txt", "r", encoding="utf-8"
    ) as f:
        text = await f.read()

    messages: list[list[str]] = []
    current_message: list[str] = []
    message_len = 0

    current_embed = ""
    embed_len = 0

    for line in text.splitlines(keepends=True):
        line_len = len(line)

        if line_len > MAX_EMBED:
            # probably won't happen but you never know...
            raise ValueError("line exceeds embed size limit")

        # new embed
        if embed_len + line_len > MAX_EMBED:
            current_message.append(current_embed)
            message_len += embed_len
            current_embed = ""
            embed_len = 0

        # new message
        if message_len + embed_len + line_len > MAX_MESSAGE:
            if embed_len:
                current_message.append(current_embed)
            messages.append(current_message)

            current_message = []
            message_len = 0
            current_embed = ""
            embed_len = 0

        current_embed += line
        embed_len += line_len

    # handle leftovers
    if embed_len:
        current_message.append(current_embed)
        # message_len += embed_len
    if current_message:
        messages.append(current_message)

    return messages


@plugin.include
@arc.slash_command("copypasta", "So tell me Frank!")
async def gerry_command(
    ctx: BlockbotContext,
    copypasta: arc.Option[
        str,
        arc.StrParams(
            "Copypasta",
            choices=[
                os.path.splitext(file)[0] for file in os.listdir("./src/copypastas")
            ],
        ),
    ] = "gerry",
) -> None:
    """Send a copypasta!"""

    messages_blocks = await load_text(copypasta)

    embeds = [
        hikari.Embed(
            description=embed_text,
            colour=Colour.GERRY_YELLOW,
        )
        for embed_text in messages_blocks[0]
    ]
    response = await ctx.respond(embeds=embeds)
    message = await response.retrieve_message()

    for message_block in messages_blocks[1:]:
        embeds = [
            hikari.Embed(
                description=embed_text,
                colour=Colour.GERRY_YELLOW,
            )
            for embed_text in message_block
        ]
        message = await ctx.client.rest.create_message(
            ctx.channel_id,
            embeds=embeds,
            reply=message,
        )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
