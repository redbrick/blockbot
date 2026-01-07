import aiohttp
import arc
import hikari
import miru

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

MAX_EMBED = 4096
MAX_DROPDOWN_OPTIONS = 25

plugin = BlockbotPlugin(name="Timetable")

timetable = plugin.include_slash_group(
    "timetable", "Get timetable information from https://timetable.redbrick.dcu.ie/"
)


async def _get_matching_fields(
    timetable_type: str, user_data: str, session: aiohttp.ClientSession
) -> tuple[list[dict[str, str]], int]:
    """Fetch matching fields from the timetable API using the ?query."""
    async with session.get(
        f"https://timetable.redbrick.dcu.ie/api/all/{timetable_type}?query={user_data}"
    ) as resp:
        return await resp.json(), resp.status


async def _get_ics_link(timetable_type: str, match: dict[str, str]) -> str:
    """Generate the ICS link for the matched timetable using its identity."""
    if timetable_type not in {"club", "society"}:
        ics_url = f"https://timetable.redbrick.dcu.ie/api?{timetable_type!s}s={match.get('identity', '')}"
    else:
        if timetable_type == "society":
            timetable_type = "societie"
        ics_url = f"https://timetable.redbrick.dcu.ie/api/cns?{timetable_type!s}s={match.get('identity', '')}"

    return ics_url


async def _timetable_response(
    ctx: BlockbotContext,
    timetable_type: str,
    user_data: str,
    matching_fields: list[dict[str, str]],
    miru_client: miru.Client,
) -> None:
    """Handle the timetable response based on the number of matches."""

    # Display a message and ask for clarification if there are more than 25 matches.
    if len(matching_fields) > MAX_DROPDOWN_OPTIONS:
        base_text = f"Multiple {timetable_type!s}s matched your query. Please be more specific:\n"
        choices_lines = [
            f"- {item.get('name', '')} (ID: {item.get('identity', '')})"
            for item in matching_fields
        ]
        choices_str = ""
        for line in choices_lines:
            if len(base_text) + len(choices_str) + len(line) + 4 > MAX_EMBED:
                choices_str += "\n..."
                break
            choices_str += line + "\n"

        embed = hikari.Embed(
            title="Multiple Matches Found",
            description=base_text + choices_str,
            color=Colour.GERRY_YELLOW,
        )
        await ctx.respond(embed=embed)
        return

    # Display a dropdown if there are between 2 and 25 matches.
    if 1 < len(matching_fields) <= MAX_DROPDOWN_OPTIONS:

        class TimetableSelectView(miru.View):
            def __init__(self, user_id: int) -> None:
                self.user_id = user_id
                super().__init__(timeout=60)

            @miru.text_select(
                custom_id="timetable_select",
                placeholder="Choose an option..",
                min_values=1,
                max_values=1,
                options=[
                    miru.SelectOption(
                        label=item.get("name", ""),
                        value=item.get("identity", ""),
                        description=f"ID: {item.get('identity', '')}",
                    )
                    for item in matching_fields
                ],
            )
            async def on_select(
                self, ctx_sub: miru.ViewContext, select: miru.TextSelect
            ) -> None:
                selected_id = select.values[0]
                # Delete original message
                await ctx_sub.message.delete()
                # Recalling the timetable response with the selected option
                await _timetable_response(
                    ctx,
                    timetable_type,
                    user_data,
                    [
                        {
                            "name": next(
                                item.get("name", "")
                                for item in matching_fields
                                if item.get("identity", "") == selected_id
                            ),
                            "identity": select.values[0],
                        }
                    ],
                    miru_client,
                )

            async def view_check(self, ctx_sub: miru.ViewContext) -> bool:
                # This view will only handle interactions that belong to the
                # user who originally ran the command.
                # For every other user they will receive an error message.
                if ctx_sub.user.id != self.user_id:
                    await ctx_sub.respond(
                        "You can't press this!",
                        flags=hikari.MessageFlag.EPHEMERAL,
                    )
                    return False

                return True

            async def on_timeout(self) -> None:
                message = self.message

                # Since the view is bound to a message, we can assert it's not None
                assert message

                await message.edit("Interaction Timed Out", components=[], embed=None)
                self.stop()

        embed = hikari.Embed(
            title="Multiple Matches Found",
            description="Please select the correct option from the dropdown below.",
            color=Colour.GERRY_YELLOW,
        )
        view = TimetableSelectView(ctx.user.id)
        response = await ctx.respond(embed=embed, components=view)
        miru_client.start_view(view, bind_to=await response.retrieve_message())
        return

    # Display the timetable ICS link if there is exactly one match.
    if len(matching_fields) == 1:
        match: dict[str, str] = matching_fields[0]
        ics_url = await _get_ics_link(timetable_type, match)

        embed = hikari.Embed(
            title=f"Timetable for {match.get('name', '')}",
            description=f"[Download ICS]({ics_url}) \n \n URL for calendar subscription: ```{ics_url}```",
            color=Colour.BRICKIE_BLUE,
        ).set_footer(text="Powered by TimetableSync")

        await ctx.respond(embed=embed)
        return

    embed = hikari.Embed(
        title=f"{str(timetable_type).capitalize()} Not Found",
        description=f"No {timetable_type!s} found matching '{user_data}'. Please check the {timetable_type!s} code/name and try again",
        color=Colour.REDBRICK_RED,
    )
    await ctx.respond(embed=embed)


async def send_timetable_info(
    ctx: BlockbotContext,
    timetable_type: str,
    user_data: str,
    miru_client: miru.Client,
    session_client: aiohttp.ClientSession,
) -> None:
    """Send timetable information based on the type and user data provided."""
    matching_fields, status = await _get_matching_fields(
        timetable_type, user_data, session_client
    )

    if status != 200:
        await ctx.respond(
            f"❌ Failed to fetch timetable data. Status code: `{status}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await _timetable_response(
        ctx, timetable_type, user_data, matching_fields, miru_client
    )


@timetable.include
@arc.slash_subcommand(
    "course", "Allows you to get the timetable for a course using the course code."
)
async def course_command(
    ctx: BlockbotContext,
    course_id: arc.Option[
        str,
        arc.StrParams(
            description="The course code. E.g. 'COMSCI1'.", min_length=3, max_length=12
        ),
    ],
    miru_client: miru.Client = arc.inject(),
    session_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await send_timetable_info(ctx, "course", course_id, miru_client, session_client)


@timetable.include
@arc.slash_subcommand(
    "module", "Allows you to get the timetable for a module using the module code."
)
async def module_command(
    ctx: BlockbotContext,
    module_id: arc.Option[
        str,
        arc.StrParams(
            description="The module code. E.g. 'ACC1005'.", min_length=3, max_length=12
        ),
    ],
    miru_client: miru.Client = arc.inject(),
    session_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await send_timetable_info(ctx, "module", module_id, miru_client, session_client)


@timetable.include
@arc.slash_subcommand(
    "location",
    "Allows you to get the timetable for a location using its location code.",
)
async def location_command(
    ctx: BlockbotContext,
    location_id: arc.Option[
        str,
        arc.StrParams(
            description="The location code. E.g. 'AHC.CG01'.",
            min_length=3,
            max_length=12,
        ),
    ],
    miru_client: miru.Client = arc.inject(),
    session_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await send_timetable_info(ctx, "location", location_id, miru_client, session_client)


@timetable.include
@arc.slash_subcommand(
    "club", "Allows you to get the timetable for a Specific club using its name."
)
async def club_command(
    ctx: BlockbotContext,
    club_name: arc.Option[
        str,
        arc.StrParams(
            description="The club name. E.g. 'Archery Club'.",
            min_length=3,
            max_length=12,
        ),
    ],
    miru_client: miru.Client = arc.inject(),
    session_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await send_timetable_info(ctx, "club", club_name, miru_client, session_client)


@timetable.include
@arc.slash_subcommand(
    "society", "Allows you to get the timetable for a specific society using its name."
)
async def society_command(
    ctx: BlockbotContext,
    society_name: arc.Option[
        str,
        arc.StrParams(
            description="The society name. E.g. 'Redbrick'.",
            min_length=3,
            max_length=12,
        ),
    ],
    miru_client: miru.Client = arc.inject(),
    session_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await send_timetable_info(ctx, "society", society_name, miru_client, session_client)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
