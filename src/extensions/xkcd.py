import arc
import hikari
import aiohttp
import random

xkcd = arc.GatewayPlugin(name="xkcd")


async def get_max_comics():
    """
    Get the latest xkcd comic number.
    """
    request_url = "https://xkcd.com/info.0.json"
    async with aiohttp.ClientSession().get(request_url) as query:
        if query.status != 200:
            return
        response = await query.json()
        return response["num"]


@xkcd.include
@arc.slash_command("xkcd", "Wisdom from xkcd!")
async def xkcd_command(
    ctx: arc.GatewayContext,
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

    base_url = "https://xkcd.com/"
    page_url = f"{base_url}{num}/"
    api_url = f"{page_url}info.0.json"

    async with aiohttp_client.get(api_url) as response:
        if response.status != 200:
            await ctx.respond(
                f"❌ Failed to query xkcd API. Status code: `{query.status}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        data = await response.json()

    if transcript:
        description = data["transcript"]
    else:
        description = ""

    embed = hikari.Embed(
        title=data["title"],
        description=description,
        url=page_url,
    )
    embed = embed.set_image(data["img"])
    embed = embed.set_author(name=f"xkcd #{num}")

    await ctx.respond(embed)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(xkcd)
