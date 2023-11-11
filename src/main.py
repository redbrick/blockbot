"""
Entrypoint script to load extensions and start the client.
"""
import os
import sys
from interactions import *
from loguru import logger
from config import DEBUG, DEV_GUILD, TOKEN

if __name__ == "__main__":
    if not TOKEN:
        logger.critical("TOKEN environment variable not set. Exiting.")
        sys.exit(1)

    logger.debug("Debug mode is %s; You can safely ignore this.", DEBUG)

    # Initialize the client
    client = Client(
        token=TOKEN,
        activity=Activity(
            name="Webgroup issues", type=ActivityType.WATCHING
        ),
        debug_scope=DEV_GUILD,
        auto_defer=True,
        sync_ext=True,
    )

    # Enable built-in extensions
    client.load_extension("interactions.ext.jurigged") # Hot reloading

    # Load custom extensions

    extensions = [
        f"extensions.{f[:-3]}"
        for f in os.listdir("src/extensions")
        if f.endswith(".py") and not f.startswith("_")
    ]

    for extension in extensions:
        try:
            client.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except errors.ExtensionLoadException as e:
            logger.exception(f"Failed to load extension: {extension}", exc_info=e)

    # Start the client

    @listen()
    async def on_startup():
        logger.info(f"Logged in as {client.user}")

    client.start()
