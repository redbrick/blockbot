import aiohttp
import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Get Timetable Command")

timetable = plugin.include_slash_group(
    "timetable", "Get Timetable's ics files and urls."
)

TIMETABLE_CACHE = {}

TIMETABLE_ENDPOINTS = {
    "course": "https://timetable.redbrick.dcu.ie/api/all/course",
    "module": "https://timetable.redbrick.dcu.ie/api/all/module",
    "location": "https://timetable.redbrick.dcu.ie/api/all/location",
    "club": "https://timetable.redbrick.dcu.ie/api/all/club",
    "society": "https://timetable.redbrick.dcu.ie/api/all/society",
}


async def fetch_and_cache_timetable_data() -> None:
    async with aiohttp.ClientSession() as session:
        for key, url in TIMETABLE_ENDPOINTS.items():
            async with session.get(url) as resp:
                if resp.status == 200:
                    TIMETABLE_CACHE[key] = await resp.json()
                else:
                    TIMETABLE_CACHE[key] = []


async def send_timetable_info(
    ctx: BlockbotContext, timetable_type: str, user_data: str
) -> None:
    if not TIMETABLE_CACHE:
        await fetch_and_cache_timetable_data()

    matching_fields = [
        item
        for item in TIMETABLE_CACHE.get(timetable_type, [])
        if user_data.lower() in item.get("name", "").lower()
    ]

    if len(matching_fields) > 1:
        max_length = 4096
        base_text = f"Multiple {timetable_type!s}s matched your query. Please be more specific:\n"
        choices_lines = [
            f"- {item.get('name', '')} (ID: {item.get('identity', '')})"
            for item in matching_fields
        ]
        choices_str = ""
        for line in choices_lines:
            if len(base_text) + len(choices_str) + len(line) + 4 > max_length:
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
    if len(matching_fields) == 1:
        match = matching_fields[0]
        if timetable_type not in {"club", "society"}:
            ics_url = f"https://timetable.redbrick.dcu.ie/api?{timetable_type!s}s={match.get('identity', '')}"
        else:
            if timetable_type == "society":
                timetable_type = "societie"
            ics_url = f"https://timetable.redbrick.dcu.ie/api/cns?{timetable_type!s}s={match.get('identity', '')}"

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
) -> None:
    await send_timetable_info(ctx, "course", course_id)


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
) -> None:
    await send_timetable_info(ctx, "module", module_id)


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
) -> None:
    await send_timetable_info(ctx, "location", location_id)


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
) -> None:
    await send_timetable_info(ctx, "club", club_name)


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
) -> None:
    await send_timetable_info(ctx, "society", society_name)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
