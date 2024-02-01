import time as t

start_time = t.time()

import arc
import hikari
import datetime as dt

plugin = arc.GatewayPlugin("Blockbot Uptime")

@plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx):
    await ctx.respond(f"Uptime: **{dt.timedelta(seconds=(t.time()-start_time) // 1)!s}**")

@arc.loader
def loader(client):
    client.add_plugin(plugin)
