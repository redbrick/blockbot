from datetime import datetime

import arc

start_time = datetime.now()

plugin = arc.GatewayPlugin("Blockbot Uptime")

@plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx):
    up_time = datetime.now() - start_time
    d = up_time.days
    h, ms = divmod(up_time.seconds, 3600)
    m, s = divmod(ms, 60)

    format = lambda val, str: f"{val} {str}{'s' if val != 1 else ''}"
    message_parts = [(d, "day"), (h, "hour"), (m, "minute"), (s, "second")]
    formatted_parts = [format(val, str) for val, str in message_parts if val]

    await ctx.respond(f"Uptime: **{', '.join(formatted_parts)}**")

@arc.loader
def loader(client):
    client.add_plugin(plugin)