import arc
import hikari
import re
import aiohttp
from urllib.parse import urlparse

from src.utils import role_mention, hedgedoc_login
from src.hooks import restrict_to_channels, restrict_to_roles
from src.config import CHANNEL_IDS, ROLE_IDS, UID_MAPS


action_items = arc.GatewayPlugin(name="Action Items")


@action_items.include
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["action-items"]]))
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command(
    "action_items",
    "Display the action items from the MD",
    is_dm_enabled=False,
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def get_action_items(
    ctx: arc.GatewayContext,
    url: arc.Option[str, arc.StrParams("URL of the minutes from the MD")],
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Display the action items from the MD!"""

    if "https://md.redbrick.dcu.ie" not in url:
        await ctx.respond(
            f"❌ `{url}` is not a valid MD URL. Please provide a valid URL.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await hedgedoc_login(aiohttp_client)

    parsed_url = urlparse(url)
    request_url = (
        f"{parsed_url.scheme}://{parsed_url.hostname}{parsed_url.path}/download"
    )

    async with aiohttp_client.get(request_url) as response:
        if response.status != 200:
            await ctx.respond(
                f"❌ Failed to fetch the minutes. Status code: `{response.status}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        content = await response.text()

    # extract the action items section from the minutes
    action_items_section = re.search(
        r"# Action Items:?\n(.*?)(\n# |\n---|$)", content, re.DOTALL
    )

    if not action_items_section:
        await ctx.respond(
            "❌ No `Action Items` section found.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # Get the matched content (excluding the "Action Items" heading itself)
    action_items_content = action_items_section.group(1)

    # extract each bullet point without the bullet point itself
    bullet_points = re.findall(r"^\s*[-*]\s+(.+)", action_items_content, re.MULTILINE)

    # format each bullet point separately in a list
    formatted_bullet_points = [
        "- " + re.sub(r"^\[.\]\s+", "", item) for item in bullet_points
    ]

    # Replace user names with user mentions
    for i, item in enumerate(formatted_bullet_points):
        for name, uid in UID_MAPS.items():
            item = item.replace(f"`{name}`", f"<@{uid}>")
        formatted_bullet_points[i] = item

    # Replace role names with role mentions
    for i, item in enumerate(formatted_bullet_points):
        for role, role_id in ROLE_IDS.items():
            item = item.replace(f"`{role}`", role_mention(role_id))
        formatted_bullet_points[i] = item

    # Send title to the action-items channel
    await action_items.client.rest.create_message(
        CHANNEL_IDS["action-items"],
        content="# Action Items:",
    )

    # send each bullet point separately
    for item in formatted_bullet_points:
        item = await action_items.client.rest.create_message(
            CHANNEL_IDS["action-items"],
            mentions_everyone=False,
            user_mentions=True,
            role_mentions=True,
            content=item,
        )

        await action_items.client.rest.add_reaction(
            channel=item.channel_id,
            message=item.id,
            emoji="✅",
        )

    # respond with success if it executes successfully
    await ctx.respond(
        "✅ Action Items sent successfully!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    return


@action_items.listen()
async def action_item_reaction(event: hikari.GuildReactionAddEvent) -> None:
    bot_user = action_items.client.app.get_me()
    if not bot_user:  # bot_user will always be available after the bot has started
        return

    # ignore reactions by the bot, reactions that are not ✅
    # and reactions not created in the #action-items channel
    if (
        event.user_id == bot_user.id
        or event.emoji_name != "✅"
        or event.channel_id != CHANNEL_IDS["action-items"]
    ):
        return

    # retrieve the message that was reacted to
    message = action_items.client.cache.get_message(
        event.message_id
    ) or await action_items.client.rest.fetch_message(
        event.channel_id, event.message_id
    )

    # ignore messages not sent by the bot and messages with no content
    if message.author.id != bot_user.id or not message.content:
        return

    # extract user and role mentions from the message content
    mention_regex = r"<@[!&]?(\d+)>"
    mentions = re.findall(mention_regex, message.content)

    # make a list of all mentions
    mentioned_ids = [int(id_) for id_ in mentions]

    if not mentioned_ids:
        return

    member = action_items.client.cache.get_member(
        event.guild_id, event.user_id
    ) or await action_items.client.rest.fetch_member(event.guild_id, event.user_id)

    is_mentioned_user = event.user_id in mentioned_ids
    has_mentioned_role = any(role_id in mentioned_ids for role_id in member.role_ids)

    if is_mentioned_user or has_mentioned_role:
        # add strikethrough and checkmark
        updated_content = f"- ✅ ~~{message.content[1:]}~~"
        await action_items.client.rest.edit_message(
            event.channel_id, event.message_id, content=updated_content
        )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(action_items)
