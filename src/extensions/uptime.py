import time as t; starttime = t.time()
import arc
import hikari
import datetime as dt

upt_plugin = arc.GatewayPlugin("Blockbot Uptime")

@upt_plugin.include
@arc.slash_command("uptime", "Show formatted uptime of Blockbot")
async def uptime(ctx):
    await ctx.respond(f"Uptime: **{dt.timedelta(seconds=t.time()-starttime)!s}**")

@arc.loader
def loader(client):
    client.add_plugin(upt_plugin)
