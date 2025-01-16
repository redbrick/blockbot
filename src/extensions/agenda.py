import datetime
from urllib.parse import urlparse

import aiohttp
import arc
import hikari

from src.config import AGENDA_TEMPLATE_URL, CHANNEL_IDS, ROLE_IDS, UID_MAPS
from src.hooks import restrict_to_channels, restrict_to_roles
from src.utils import get_md_content, post_new_md_content, role_mention, utcnow

plugin = arc.GatewayPlugin(name="Agenda")

agenda = plugin.include_slash_group("agenda", "Interact with the agenda.")


async def generate_date_choices(
    _: arc.AutocompleteData[arc.GatewayClient, str],
) -> list[str]:
    """Generate date options for the next 7 days."""
    today = utcnow().today()
    return [
        (today + datetime.timedelta(days=i)).strftime("%A %d/%m/%Y") for i in range(7)
    ]


def generate_time_choices() -> list[str]:
    """Generate time options for every hour."""
    base_time = datetime.time(0, 0)
    times: list[str] = []

    for hour in range(24):
        current_time = (
            datetime.datetime.combine(utcnow().today(), base_time)
            + datetime.timedelta(hours=hour)
        ).time()
        times.append(current_time.strftime("%H:%M"))

    return times


@agenda.include
@arc.with_hook(
    restrict_to_channels(
        channel_ids=[
            CHANNEL_IDS["bots-cmt"],
            CHANNEL_IDS["committee-announcements"],
            CHANNEL_IDS["cowboys-and-cowgirls-committee"],
        ],
    ),
)
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand(
    "generate",
    "Generate a new agenda for committee meetings.",
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def gen_agenda(
    ctx: arc.GatewayContext,
    date: arc.Option[
        str,
        arc.StrParams("Select a date.", autocomplete_with=generate_date_choices),
    ],
    time: arc.Option[
        str,
        arc.StrParams(
            "Enter the time in HH:MM format.",
            choices=generate_time_choices(),
        ),
    ],
    room: arc.Option[
        str,
        arc.StrParams("Select a Room."),
    ],
    note: arc.Option[
        str | None, arc.StrParams("Optional note to be included in the announcement.")
    ] = None,
    url: arc.Option[
        str,
        arc.StrParams("URL of the agenda template from the MD"),
    ] = AGENDA_TEMPLATE_URL,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Generate a new agenda for committee meetings."""

    parsed_date = (
        datetime.datetime.strptime(date, "%A %d/%m/%Y")
        .replace(tzinfo=datetime.timezone.utc)
        .date()
    )
    parsed_time = (
        datetime.datetime.strptime(time, "%H:%M")
        .replace(tzinfo=datetime.timezone.utc)
        .time()
    )

    parsed_datetime = datetime.datetime.combine(parsed_date, parsed_time)

    formatted_date = parsed_datetime.strftime("%Y-%m-%d")
    formatted_time = parsed_datetime.strftime("%H:%M")
    formatted_datetime = parsed_datetime.strftime("%A, %Y-%m-%d %H:%M")

    try:
        content = await get_md_content(url, aiohttp_client)
    except Exception as e:
        await ctx.respond(
            f"❌ {e}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    modified_content = content.format(
        DATE=formatted_date,
        TIME=formatted_time,
        ROOM=room,
    )

    try:
        new_agenda_url = await post_new_md_content(modified_content, aiohttp_client)
    except Exception as e:
        await ctx.respond(
            f"❌ {e}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    announce_text = f"""
## 📣 Agenda for this week's meeting | {formatted_datetime} | {room} <:bigRed:634311607039819776>


[{formatted_date} Agenda](<{new_agenda_url}>)

- Please fill in your sections with anything you would like to discuss.
- Put your Redbrick `username` beside any agenda items you add.
- If you can't attend the meeting, please DM <@{UID_MAPS["kronos"]}> with your reason.
- React with <:bigRed:634311607039819776> if you can make it.

||{role_mention(ROLE_IDS["committee"])}||
"""
    if note:
        announce_text += f"## Note:\n{note}"

    announce = await plugin.client.rest.create_message(
        CHANNEL_IDS["committee-announcements"],
        mentions_everyone=False,
        user_mentions=True,
        role_mentions=True,
        content=announce_text,
    )

    await plugin.client.rest.add_reaction(
        channel=announce.channel_id,
        message=announce.id,
        emoji=hikari.CustomEmoji.parse("<:bigRed:634311607039819776>"),
    )

    # respond with success if it executes successfully
    await ctx.respond(
        "✅ Agenda generated. Announcement sent successfully!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    return


@agenda.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand(
    "template",
    "View the agenda template",
)
async def view_template(
    ctx: arc.GatewayContext,
) -> None:
    """View the agenda template."""

    embed = hikari.Embed(
        title="Agenda Template",
        url=AGENDA_TEMPLATE_URL,
        description="Click the link above to view the agenda template.\n\n**NOTE:** Any edits made to this template will affect the generated agenda.",
        colour=0x5865F2,
    )
    embed = embed.set_image(
        "https://cdn.redbrick.dcu.ie/hedgedoc-uploads/sonic-the-hedgedoc.png",
    )

    await ctx.respond(
        embed,
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
