from datetime import datetime

import arc

start_time = datetime.now()

plugin = arc.GatewayPlugin("Blockbot Uptime")


@plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx):
    up_time = datetime.now() - start_time
    h, ms = divmod(up_time.seconds, 3600)
    m, s = divmod(ms, 60)
    await ctx.respond(f"Uptime: **{up_time.days} days, {h} hours, {m} minutes, and {s} seconds**.")

@arc.loader
def loader(client):
    client.add_plugin(plugin)
