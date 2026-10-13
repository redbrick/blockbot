import re
from urllib.parse import urlparse

import aiohttp
import arc
import hikari

from src.config import CHANNEL_IDS, ROLE_IDS, Colour
from src.hooks import restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin
from src.utils import channel_mention

plugin = BlockbotPlugin(name="Rules")

rules = plugin.include_slash_group("rules", "Update the rules.")


def replace_channel_mentions(text: str) -> str:
    return re.sub(
        r"`#([a-zA-Z0-9_-]+)`",
        lambda m: f"{channel_mention(CHANNEL_IDS[m.group(1)])}",
        text,
    )


async def get_rules(url: str, aiohttp_client: aiohttp.ClientSession) -> str:
    """
    Get the rules from open-governance
    """
    parsed_url = urlparse(url)
    request_url = f"{parsed_url.scheme}://{parsed_url.hostname}{parsed_url.path}"

    async with aiohttp_client.get(request_url) as response:
        response.raise_for_status()
        text = await response.text()
        cleaned = re.sub(r"^---\s*[\s\S]*?\s*---\s*", "", text, count=1).strip()
        return replace_channel_mentions(cleaned)


@rules.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand(
    "update",
    "Update the discord rules from open governance.",
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def update_rules(
    ctx: BlockbotContext,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Update the discord rules from open governance."""

    url = "https://raw.githubusercontent.com/redbrick/open-governance/refs/heads/master/documents/Discord-rules.md"
    try:
        content = await get_rules(url, aiohttp_client)
    except aiohttp.ClientResponseError as e:
        await ctx.respond(
            f"❌ Failed to fetch the rules from open-governance. Status code: `{e.status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    embed = hikari.Embed(description=content, colour=Colour.REDBRICK_RED)
    embed = embed.set_thumbnail(ctx.get_guild().make_icon_url())

    await plugin.client.rest.create_message(
        CHANNEL_IDS["rules"],
        embed=embed,
    )

    await ctx.respond(f"{channel_mention(CHANNEL_IDS['rules'])} updated successfully.")


@rules.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand(
    "view",
    "View the rules",
)
async def view_rules(
    ctx: BlockbotContext,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Update the discord rules from open governance."""

    url = "https://raw.githubusercontent.com/redbrick/open-governance/refs/heads/master/documents/Discord-rules.md"
    try:
        content = await get_rules(url, aiohttp_client)
    except aiohttp.ClientResponseError as e:
        await ctx.respond(
            f"❌ Failed to fetch the rules from open-governance. Status code: `{e.status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    embed = hikari.Embed(description=content, colour=Colour.REDBRICK_RED)
    embed = embed.set_thumbnail(ctx.get_guild().make_icon_url())

    await ctx.respond(
        content=f"{channel_mention(CHANNEL_IDS['rules'])}",
        embed=embed,
    )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
