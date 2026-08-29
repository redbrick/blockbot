import arc

from src.models import BlockbotContext, BlockbotPlugin, command_loader
from src.utils import utcnow

START_TIME = utcnow()


@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx: BlockbotContext) -> None:
    up_time = utcnow() - START_TIME
    d = up_time.days
    h, ms = divmod(up_time.seconds, 3600)
    m, s = divmod(ms, 60)

    def format_time(val: int, s: str) -> str:
        return f"{val} {s}{'s' if val != 1 else ''}"

    message_parts = [(d, "day"), (h, "hour"), (m, "minute"), (s, "second")]
    formatted_parts = [format_time(val, text) for val, text in message_parts if val]

    await ctx.respond(f"Uptime: **{', '.join(formatted_parts)}**")


@command_loader
def loader(plugin: BlockbotPlugin) -> None:
    plugin.add_command(uptime)
