import arc
import hikari
import aiohttp
from urllib.parse import urlparse
import datetime

from src.utils import role_mention, hedgedoc_login
from src.hooks import restrict_to_channels, restrict_to_roles
from src.config import CHANNEL_IDS, ROLE_IDS, UID_MAPS, AGENDA_TEMPLATE_URL


plugin = arc.GatewayPlugin(name="Agenda")


def generate_date_choices():
    """Generate date options for the next 7 days."""
    today = datetime.date.today()
    return [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


def generate_time_choices():
    """Generate time options for every hour"""
    base_time = datetime.time(0, 0)
    times = []
    for hour in range(24):
        current_time = (
            datetime.datetime.combine(datetime.date.today(), base_time)
            + datetime.timedelta(hours=hour)
        ).time()
        times.append(current_time.strftime("%H:%M"))
    return times


@plugin.include
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bots-cmt"]]))
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command(
    "agenda",
    "Generate a new agenda for committee meetings",
    is_dm_enabled=False,
    autodefer=arc.AutodeferMode.EPHEMERAL,
)
async def gen_agenda(
    ctx: arc.GatewayContext,
    date: arc.Option[
        str,
        arc.StrParams("Select a date", choices=generate_date_choices()),
    ],
    time: arc.Option[
        str,
        arc.StrParams(
            "Enter the time in HH:MM format", choices=generate_time_choices()
        ),
    ],
    room: arc.Option[
        str,
        arc.StrParams("Select a Room"),
    ],
    url: arc.Option[
        str, arc.StrParams("URL of the agenda template from the MD")
    ] = AGENDA_TEMPLATE_URL,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Create a new agenda for committee meetings"""

    parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    parsed_time = datetime.datetime.strptime(time, "%H:%M").time()

    parsed_datetime = datetime.datetime.combine(parsed_date, parsed_time)

    DATE = parsed_datetime.strftime("%Y-%m-%d")
    TIME = parsed_datetime.strftime("%H:%M")
    full_datetime = parsed_datetime.strftime("%Y-%m-%d %A %H:%M")

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

    modified_content = content.format(DATE=DATE, TIME=TIME, ROOM=room)

    post_url = f"{parsed_url.scheme}://{parsed_url.hostname}/new"
    post_headers = {"Content-Type": "text/markdown"}

    async with aiohttp_client.post(
        url=post_url,
        headers=post_headers,
        data=modified_content,
    ) as response:
        if response.status != 200:
            await ctx.respond(
                f"❌ Failed to generate the agenda. Status code: `{response.status}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

    new_agenda_url = response.url
    announce_text = f"""
## 📣 Agenda for this week's meeting | {full_datetime} | {room} <:bigRed:634311607039819776>


[{DATE} Agenda](<{new_agenda_url}>)

- Please fill in your sections with anything you would like to discuss.
- Put your Redbrick `username` beside any agenda items you add.
- If you can't attend the meeting, please DM <@{UID_MAPS["kronos"]}>  with your reason.
- React with <:bigRed:634311607039819776> if you can make it.

||{role_mention(ROLE_IDS["committee"])}||
    """

    announce = await plugin.client.rest.create_message(
        CHANNEL_IDS["bots-cmt"],
        content=announce_text,
    )

    await plugin.client.rest.add_reaction(
        channel=announce.channel_id,
        message=announce.id,
        emoji=hikari.CustomEmoji(
            id=634311607039819776, name="bigRed", is_animated=False
        ),
    )

    # respond with success if it executes successfully
    await ctx.respond(
        "✅ Agenda generated. Announcement sent successfully!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    return


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
