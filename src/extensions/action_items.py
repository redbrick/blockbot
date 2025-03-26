import re

import aiohttp
import arc
import hikari

from src.config import CHANNEL_IDS, ROLE_IDS, UID_MAPS, Feature
from src.hooks import restrict_to_channels, restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin
from src.utils import get_md_content, role_mention

plugin = BlockbotPlugin(name="Action Items", required_features=[Feature.LDAP])


@plugin.include
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["action-items"]]))
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command(
    "action_items",
    "Display the action items from the MD",
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def get_action_items(
    ctx: BlockbotContext,
    url: arc.Option[str, arc.StrParams("URL of the minutes from the MD")],
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Display the action items from the MD!"""

    try:
        content = await get_md_content(url, aiohttp_client)
    except aiohttp.ClientResponseError as e:
        await ctx.respond(
            f"❌ Failed to fetch the minutes. Status code: `{e.status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    except ValueError as e:
        await ctx.respond(
            f"❌ {e}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # extract the action items section from the minutes
    action_items_section = re.search(
        r"# Action Items:?\n(.*?)(\n# |\n---|$)",
        content,
        re.DOTALL,
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
            item = item.replace(f"`{name}`", f"<@{uid}>")  # noqa: PLW2901
        formatted_bullet_points[i] = item

    # Replace role names with role mentions
    for i, item in enumerate(formatted_bullet_points):
        for role, role_id in ROLE_IDS.items():
            item = item.replace(f"`{role}`", role_mention(role_id))  # noqa: PLW2901
        formatted_bullet_points[i] = item

    # Send title to the action-items channel
    await plugin.client.rest.create_message(
        CHANNEL_IDS["action-items"],
        content="# Action Items:",
    )

    # send each bullet point separately
    for item in formatted_bullet_points:
        message = await plugin.client.rest.create_message(
            CHANNEL_IDS["action-items"],
            mentions_everyone=False,
            user_mentions=True,
            role_mentions=True,
            content=item,
        )

        await plugin.client.rest.add_reaction(
            channel=message.channel_id,
            message=message.id,
            emoji="✅",
        )

    # respond with success if it executes successfully
    await ctx.respond(
        "✅ Action Items sent successfully!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    return


async def check_valid_reaction(
    event: hikari.GuildReactionAddEvent | hikari.GuildReactionDeleteEvent,
    message: hikari.PartialMessage,
) -> bool:
    bot_user = plugin.client.app.get_me()
    if not bot_user:  # bot_user will always be available after the bot has started
        return False

    # ignore reactions by the bot, reactions that are not ✅
    # and reactions not created in the #action-items channel
    if (
        event.user_id == bot_user.id
        or event.emoji_name != "✅"
        or event.channel_id != CHANNEL_IDS["action-items"]
    ):
        return False

    assert message.author  # it will always be available

    # verify it's a message sent by the bot and has content
    return message.author.id == bot_user.id and message.content is not None


async def validate_user_reaction(
    user_id: int,
    message_content: str,
    guild_id: int,
) -> bool:
    # extract user and role mentions from the message content
    mention_regex = r"<@[!&]?(\d+)>"
    mentions = re.findall(mention_regex, message_content)

    # make a list of all mentions
    mentioned_ids = [int(id_) for id_ in mentions]

    # user is mentioned
    if user_id in mentioned_ids:
        return True

    member = plugin.client.cache.get_member(
        guild_id,
        user_id,
    ) or await plugin.client.rest.fetch_member(guild_id, user_id)

    # user's role is mentioned
    return any(role_id in mentioned_ids for role_id in member.role_ids)


@plugin.listen()
async def reaction_add(event: hikari.GuildReactionAddEvent) -> None:
    # retrieve the message that was reacted to
    message = plugin.client.cache.get_message(
        event.message_id,
    ) or await plugin.client.rest.fetch_message(
        event.channel_id,
        event.message_id,
    )

    is_valid_reaction = await check_valid_reaction(event, message)
    if not is_valid_reaction:
        return

    assert message.content  # check_valid_reaction verifies the message content exists

    is_valid_reaction = await validate_user_reaction(
        event.user_id,
        message.content,
        event.guild_id,
    )
    if not is_valid_reaction:
        return

    # cross out the action item, if it was not crossed out already
    if not message.content.startswith("- ✅ ~~"):
        # add strikethrough and checkmark
        updated_content = f"- ✅ ~~{message.content[2:]}~~"
        await plugin.client.rest.edit_message(
            event.channel_id,
            event.message_id,
            content=updated_content,
        )


@plugin.listen()
async def reaction_remove(event: hikari.GuildReactionDeleteEvent) -> None:
    # retrieve the message that was un-reacted to
    # NOTE: cannot use cached message as the reaction count will be outdated
    message = await plugin.client.rest.fetch_message(
        event.channel_id,
        event.message_id,
    )

    is_valid_reaction = await check_valid_reaction(event, message)
    if not is_valid_reaction:
        return

    assert message.content  # check_valid_reaction verifies the message content exists

    checkmark_reactions = await event.app.rest.fetch_reactions_for_emoji(
        event.channel_id,
        event.message_id,
        "✅",
    )

    reactions = [
        await validate_user_reaction(user.id, message.content, event.guild_id)
        for user in checkmark_reactions
    ]
    valid_reaction_count = len(
        list(
            filter(
                lambda r: r is True,
                reactions,
            ),
        ),
    )

    assert message.content  # check_valid_reaction verifies the message content exists
    # remove the strikethrough on the item, provided all mentioned users/roles
    # are not currently reacted to the message
    if message.content.startswith("- ✅ ~~") and valid_reaction_count == 0:
        # add strikethrough and checkmark
        updated_content = f"- {message.content[6:-2]}"
        await plugin.client.rest.edit_message(
            event.channel_id,
            event.message_id,
            content=updated_content,
        )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
