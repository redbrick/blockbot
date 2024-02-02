import logging
import sys

import arc
import hikari

from src.config import DEBUG, TOKEN

if TOKEN is None:
    print("TOKEN environment variable not set. Exiting.")
    sys.exit(1)

bot = hikari.GatewayBot(
    token=TOKEN,
    banner=None,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
    logs="DEBUG" if DEBUG else "INFO",
)

logging.info(f"Debug mode is {DEBUG}; You can safely ignore this.")

client = arc.GatewayClient(bot, is_dm_enabled=False)
client.load_extensions_from("./src/extensions/")


@client.set_error_handler
async def error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    if DEBUG:
        message = f"```{exc}```"
    else:
        message = "If this persists, create an issue at <https://webgroup-issues.redbrick.dcu.ie/>."

    await ctx.respond(f"❌ Blockbot encountered an unhandled exception. {message}")
    logging.error(exc)

    raise exc
