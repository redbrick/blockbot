import random

import aiohttp
import arc
import hikari

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

xkcd = BlockbotPlugin(name="xkcd")


@xkcd.include
@arc.slash_command("xkcd", "Wisdom from xkcd!")
async def xkcd_command(
    ctx: BlockbotContext,
    num: arc.Option[
        int | None, arc.IntParams("Optionally specify an xkcd number.")
    ] = None,
    transcript: arc.Option[bool, arc.BoolParams("Show the transcript?")] = False,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Send an xkcd!"""
    if num is None:
        latest_url = "https://xkcd.com/info.0.json"
        async with aiohttp_client.get(latest_url) as query:
            if query.status != 200:
                await ctx.respond(
                    f"❌ Failed to query xkcd API. Status code: `{query.status}`",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
                return

            response = await query.json()
            max_comic = response["num"]

        num = random.randint(1, max_comic)

    page_url = f"https://xkcd.com/{num}"
    api_url = f"{page_url}/info.0.json"

    async with aiohttp_client.get(api_url) as response:
        if response.status != 200:
            await ctx.respond(
                f"❌ Failed to query xkcd API. Status code: `{response.status}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        data = await response.json()

    # sometimes transcript is an empty string
    transcript_text = t if (t := data["transcript"]) else "No transcript available."

    embed = hikari.Embed(
        title=data["title"],
        description=transcript_text if transcript else None,
        url=page_url,
    )
    embed = embed.set_image(data["img"])
    embed = embed.set_author(name=f"xkcd #{num}")

    await ctx.respond(embed)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(xkcd)
