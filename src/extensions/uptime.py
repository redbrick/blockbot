import time as t; starttime = t.time()
import arc
import hikari
import datetime as dt

uptime_plugin = arc.GatewayPlugin("Blockbot Uptime")

@uptime_plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx):
    await ctx.respond(f"Uptime: **{dt.timedelta(seconds=t.time()-starttime)!s}**")

@arc.loader
def loader(client):
    client.add_plugin(uptime_plugin)
