import logging

import arc
import hikari
from sqlalchemy.ext.asyncio import AsyncEngine

from src.config import DEBUG, TOKEN
from src.database import Base, engine

bot = hikari.GatewayBot(
    token=TOKEN,
    banner=None,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
    logs="DEBUG" if DEBUG else "INFO",
)

logging.info(f"Debug mode is {DEBUG}; You can safely ignore this.")

client = arc.GatewayClient(bot, is_dm_enabled=False)
client.load_extensions_from("./src/extensions/")

@client.set_startup_hook
async def startup_hook(client: arc.GatewayClient) -> None:
    client.set_type_dependency(AsyncEngine, engine)

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# TODO: fix bug where commands that error are respond to twice
# (Once by our message, once by built-in response)
@client.set_error_handler
async def error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    if DEBUG:
        message = f"```{exc}```"
    else:
        message = "If this persists, create an issue at <https://webgroup-issues.redbrick.dcu.ie/>."

    await ctx.respond(f"❌ Blockbot encountered an unhandled exception. {message}")
    logging.error(exc)

    raise exc
