import contextlib
import datetime
import typing

import aiohttp
import arc
import hikari
import miru
from hikari.impl.special_endpoints import PollBuilder

from src.config import AGENDA_TEMPLATE_URL, CHANNEL_IDS, ROLE_IDS, UID_MAPS, Feature
from src.hooks import restrict_to_channels, restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin
from src.utils import (
    get_md_content,
    post_new_md_content,
    role_mention,
    utcnow,
)

plugin = BlockbotPlugin(name="Agenda", required_features=[Feature.LDAP])

agenda = plugin.include_slash_group("agenda", "Interact with the agenda.")

POLL_MODE_CHOICES = ["yes_no", "custom"]
CUSTOM_POLL_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


async def generate_date_choices(
    _: arc.AutocompleteData[arc.GatewayClient, str],
) -> list[str]:
    """Generate date options for the next 7 days."""
    today = utcnow().today()
    return [
        (today + datetime.timedelta(days=i)).strftime("%A %d/%m/%Y") for i in range(7)
    ]


async def generate_time_autocomplete(
    ctx: arc.AutocompleteData[arc.GatewayClient, str],
) -> list[str]:
    """Generate up to 25 matching half-hour time suggestions."""
    base_time = datetime.time(0, 0)
    times = [
        (
            datetime.datetime.combine(utcnow().today(), base_time)
            + datetime.timedelta(minutes=interval * 30)
        ).strftime("%H:%M")
        for interval in range(48)
    ]
    if ctx.focused_value:
        focused_value = str(ctx.focused_value).strip()
        times = [time for time in times if focused_value in time]
    return times[:25]


def parse_custom_poll_options(raw_options: str | None) -> list[str] | None:
    """Parse custom poll options into a unique list."""
    if not raw_options:
        return None

    parsed_options = [opt.strip() for opt in raw_options.split(",") if opt.strip()]
    unique_options = list(dict.fromkeys(parsed_options))

    if not 2 <= len(unique_options) <= 5:
        return None
    return unique_options


async def post_reaction_poll(*, question: str, options: list[str]) -> None:
    """Post a reaction-based poll in committee-announcements."""
    option_emojis = ["👍", "👎"] if options == ["Yes", "No"] else CUSTOM_POLL_EMOJIS
    selected_emojis = option_emojis[: len(options)]

    poll_lines = "\n".join(
        f"{emoji} {option}"
        for emoji, option in zip(selected_emojis, options, strict=True)
    )
    poll_message = await plugin.client.rest.create_message(
        CHANNEL_IDS["committee-announcements"],
        mentions_everyone=False,
        user_mentions=False,
        role_mentions=False,
        content=f"## 📊 Poll: {question}\n{poll_lines}\n\nReact below to vote.",
    )

    for emoji in selected_emojis:
        await plugin.client.rest.add_reaction(
            channel=poll_message.channel_id,
            message=poll_message.id,
            emoji=emoji,
        )


async def post_poll(*, question: str, options: list[str]) -> None:
    """Post a native Discord poll, falling back to reactions if unavailable."""
    try:
        poll = PollBuilder(
            question_text=question,
            allow_multiselect=False,
            duration=24,
        )
        for option in options:
            poll.add_answer(text=option)

        await plugin.client.rest.create_message(
            CHANNEL_IDS["committee-announcements"],
            poll=poll,
        )
        return
    except Exception:
        pass

    await post_reaction_poll(question=question, options=options)


class AgendaConfirmView(miru.View):
    def __init__(
        self,
        *,
        author_id: int,
        on_confirm: typing.Callable[[], typing.Awaitable[str]],
    ) -> None:
        self.author_id = author_id
        self.on_confirm = on_confirm
        super().__init__(timeout=120)

    async def disable_all(self) -> None:
        for item in self.children:
            item.disabled = True

        if self.message is None:
            return

        with contextlib.suppress(hikari.NotFoundError):
            await self.message.edit(components=self)

    async def on_timeout(self) -> None:
        await self.disable_all()
        self.stop()

    @miru.button(
        label="Confirm", style=hikari.ButtonStyle.SUCCESS, custom_id="agenda_confirm"
    )
    async def confirm_post(self, ctx: miru.ViewContext, _: miru.Button) -> None:
        if ctx.user.id != self.author_id:
            await ctx.respond(
                "You are not allowed to confirm this action.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        try:
            response_text = await self.on_confirm()
        except aiohttp.ClientResponseError as error:
            response_text = (
                "❌ Failed to post agenda/poll. "
                f"Upstream returned status `{error.status}`."
            )
        except Exception:
            response_text = "❌ Failed to post agenda/poll due to an unexpected error."
        await self.disable_all()
        await ctx.edit_response(response_text, components=self)
        self.stop()

    @miru.button(
        label="Cancel", style=hikari.ButtonStyle.DANGER, custom_id="agenda_cancel"
    )
    async def cancel_post(self, ctx: miru.ViewContext, _: miru.Button) -> None:
        if ctx.user.id != self.author_id:
            await ctx.respond(
                "You are not allowed to cancel this action.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        await self.disable_all()
        await ctx.edit_response("❌ Agenda generation cancelled.", components=self)
        self.stop()


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
async def gen_agenda(  # noqa: PLR0911, PLR0915
    ctx: BlockbotContext,
    date: arc.Option[
        str,
        arc.StrParams("Select a date.", autocomplete_with=generate_date_choices),
    ],
    time: arc.Option[
        str,
        arc.StrParams(
            "Enter the time in HH:MM format.",
            autocomplete_with=generate_time_autocomplete,
        ),
    ],
    room: arc.Option[
        str,
        arc.StrParams("Select a Room."),
    ],
    note: arc.Option[
        str | None, arc.StrParams("Optional note to be included in the announcement.")
    ] = None,
    add_poll: arc.Option[
        bool,
        arc.BoolParams("Add a poll to committee-announcements?"),
    ] = False,
    poll_mode: arc.Option[
        str,
        arc.StrParams(
            "Poll mode (`yes_no` or `custom`).",
            choices=POLL_MODE_CHOICES,
        ),
    ] = "yes_no",
    poll_question: arc.Option[
        str | None,
        arc.StrParams("Poll question (required when `add_poll` is enabled)."),
    ] = None,
    poll_options: arc.Option[
        str | None,
        arc.StrParams("Comma-separated custom poll options (2-5 options)."),
    ] = None,
    url: arc.Option[
        str,
        arc.StrParams("URL of the agenda template from the MD"),
    ] = AGENDA_TEMPLATE_URL,  # pyright: ignore[reportArgumentType] - it is guaranteed to exist because of runtime checks!
    miru_client: miru.Client = arc.inject(),
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    """Generate a new agenda for committee meetings."""

    parsed_date = (
        datetime.datetime.strptime(date, "%A %d/%m/%Y")
        .replace(tzinfo=datetime.timezone.utc)
        .date()
    )
    try:
        parsed_time = (
            datetime.datetime.strptime(time, "%H:%M")
            .replace(tzinfo=datetime.timezone.utc)
            .time()
        )
    except ValueError:
        await ctx.respond(
            "❌ Invalid time format. Please use `HH:MM` (e.g. `18:30`).",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    parsed_datetime = datetime.datetime.combine(parsed_date, parsed_time)

    formatted_date = parsed_datetime.strftime("%Y-%m-%d")
    formatted_time = parsed_datetime.strftime("%H:%M")
    formatted_datetime = parsed_datetime.strftime("%A, %Y-%m-%d %H:%M")

    parsed_poll_options: list[str] = []
    if add_poll:
        cleaned_question = (poll_question or "").strip()
        if not cleaned_question:
            await ctx.respond(
                "❌ `poll_question` is required when `add_poll` is enabled.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        if poll_mode == "custom":
            custom_options = parse_custom_poll_options(poll_options)
            if custom_options is None:
                await ctx.respond(
                    "❌ `poll_options` must contain 2-5 unique, non-empty comma-separated values.",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
                return
            parsed_poll_options = custom_options
        else:
            parsed_poll_options = ["Yes", "No"]

    try:
        content = await get_md_content(url, aiohttp_client)
    except aiohttp.ClientResponseError as e:
        await ctx.respond(
            f"❌ Failed to fetch the agenda template. Status code: `{e.status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    except ValueError as e:
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
    except aiohttp.ClientResponseError as e:
        await ctx.respond(
            f"❌ Failed to generate the agenda. Status code: `{e.status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    announce_text = f"""
## 📣 Agenda for this week's meeting | {formatted_datetime} | {room} <:bigRed:634311607039819776>


[{formatted_date} Agenda](<{new_agenda_url}>)

- Please fill in your sections with anything you would like to discuss.
- Put your Redbrick `username` beside any agenda items you add.
- If you can't attend the meeting, please DM {f"<@{UID_MAPS['secretary']}>" if "secretary" in UID_MAPS else "the secretary"} or {f"<@{UID_MAPS['chair']}>" if "chair" in UID_MAPS else "the chairperson"} with your reason.
- React with <:bigRed:634311607039819776> if you can make it.

||{role_mention(ROLE_IDS["committee"])}||
"""
    if note:
        announce_text += f"## Note:\n{note}"

    async def send_agenda_and_poll() -> str:
        announce = await plugin.client.rest.create_message(
            CHANNEL_IDS["committee-announcements"],
            mentions_everyone=False,
            user_mentions=True,
            role_mentions=True,
            content=announce_text,
        )

        try:
            await plugin.client.rest.add_reaction(
                channel=announce.channel_id,
                message=announce.id,
                emoji=hikari.CustomEmoji.parse("<:bigRed:634311607039819776>"),
            )
        except hikari.BadRequestError, hikari.NotFoundError, hikari.ForbiddenError:
            await plugin.client.rest.add_reaction(
                channel=announce.channel_id,
                message=announce.id,
                emoji="🧱",
            )

        if add_poll:
            await post_poll(
                question=(poll_question or "").strip(),
                options=parsed_poll_options,
            )
            return "✅ Agenda generated and poll posted successfully!"

        return "✅ Agenda generated. Announcement sent successfully!"

    if not add_poll:
        await ctx.respond(
            await send_agenda_and_poll(),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    preview_options = "\n".join(f"- {option}" for option in parsed_poll_options)
    confirmation_text = (
        "## Confirm agenda + poll post\n"
        f"- Date/Time: `{formatted_datetime}`\n"
        f"- Room: `{room}`\n"
        f"- Poll mode: `{poll_mode}`\n"
        f"- Poll question: `{(poll_question or '').strip()}`\n"
        f"- Poll options:\n{preview_options}\n\n"
        "Use the buttons below to confirm or cancel."
    )

    view = AgendaConfirmView(author_id=ctx.user.id, on_confirm=send_agenda_and_poll)
    response = await ctx.respond(
        confirmation_text,
        flags=hikari.MessageFlag.EPHEMERAL,
        components=view,
    )
    miru_client.start_view(view, bind_to=await response.retrieve_message())
    return


@agenda.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand(
    "template",
    "View the agenda template",
)
async def view_template(ctx: BlockbotContext) -> None:
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
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
