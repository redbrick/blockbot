import logging
import sys

import arc
import hikari

from src.config import DEBUG, TOKEN

if TOKEN is None:
    logging.critical("TOKEN environment variable not set. Exiting.")
    sys.exit(1)

logging.debug(f"Debug mode is {DEBUG}; You can safely ignore this.")

bot = hikari.GatewayBot(
    token=TOKEN,
    banner=None,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
    logs="DEBUG" if DEBUG else "INFO",
)

arc_client = arc.GatewayClient(bot)
arc_client.load_extensions_from("./src/extensions/")
