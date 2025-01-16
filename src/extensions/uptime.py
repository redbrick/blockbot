import arc

from src.utils import utcnow

start_time = utcnow()

plugin = arc.GatewayPlugin("Blockbot Uptime")


@plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx: arc.GatewayContext) -> None:
    up_time = utcnow() - start_time
    d = up_time.days
    h, ms = divmod(up_time.seconds, 3600)
    m, s = divmod(ms, 60)

    def format_time(val: int, s: str) -> str:
        return f"{val} {s}{'s' if val != 1 else ''}"

    message_parts = [(d, "day"), (h, "hour"), (m, "minute"), (s, "second")]
    formatted_parts = [format_time(val, text) for val, text in message_parts if val]

    await ctx.respond(f"Uptime: **{', '.join(formatted_parts)}**")


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
