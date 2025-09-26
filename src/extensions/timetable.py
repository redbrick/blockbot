import collections
import itertools
import aiohttp
import arc
import hikari

from src.config import Colour
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Get Timetable Command")

timetables = plugin.include_slash_group("timetables", "Get Timetable's ics files and urls.")

TIMETABLE_CACHE = {}

TIMETABLE_ENDPOINTS = {
    "course": "https://timetable.redbrick.dcu.ie/api/all/course",
    "module": "https://timetable.redbrick.dcu.ie/api/all/module",
    "location": "https://timetable.redbrick.dcu.ie/api/all/location",
    "club": "https://timetable.redbrick.dcu.ie/api/all/club",
    "society": "https://timetable.redbrick.dcu.ie/api/all/society",
}

async def fetch_and_cache_timetable_data():
    async with aiohttp.ClientSession() as session:
        for key, url in TIMETABLE_ENDPOINTS.items():
            async with session.get(url) as resp:
                if resp.status == 200:
                    TIMETABLE_CACHE[key] = await resp.json()
                else:
                    TIMETABLE_CACHE[key] = []

@timetables.include
@arc.slash_subcommand("course", "Allows you to get the timetable for a subject using the course code.")
async def timetable_command(
    ctx: BlockbotContext,
    course_id: arc.Option[
        str, arc.StrParams(description="The course code. E.g. 'COMSCI1'.", min_length=3, max_length=12)
    ],
    ) -> None:
    # Ensure cache is populated
    if not TIMETABLE_CACHE:
        await fetch_and_cache_timetable_data()

    matching_courses = [
        item for item in TIMETABLE_CACHE.get("course", [])
        if course_id.lower() in item.get("name", "").lower()
    ]

    if len(matching_courses) > 1:
        choices = "\n".join(
            f"- {item.get('name', '')} (ID: {item.get('identity', '')})"
            for item in matching_courses
        )

        embed = hikari.Embed(
            title="Multiple Matches Found",
            description=f"Multiple courses matched your query. Please be more specific or use the ID:\n{choices}",
            color=Colour.GERRY_YELLOW,
        )
        await ctx.respond(embed=embed)
        return
    elif len(matching_courses) == 1:
        course = matching_courses[0]
        ics_url = f"https://timetable.redbrick.dcu.ie/api?courses={course.get('identity', '')}"
        embed = hikari.Embed(
            title=f"Timetable for {course.get('name', '')}",
            description=f"[Download ICS]({ics_url}) \n \n URL for calendar subscription: ```{ics_url}```",
            color=Colour.BRICKIE_BLUE,
        ).set_footer(text="Powered by TimetableSync")
        await ctx.respond(embed=embed)
        return

    embed = hikari.Embed(
        title="Course Not Found",
        description=f"No course found matching '{course_id}'. Please check the course code and try again", 
        color=Colour.REDBRICK_RED,
    )
    await ctx.respond(embed=embed)

@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)

