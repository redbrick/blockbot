"""
Entrypoint script to load extensions and start the client.
"""
import sys
import glob
import interactions as discord
from loguru import logger
from pathlib import Path
from config import DEBUG, TOKEN

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stdout, level="DEBUG" if DEBUG else "INFO")

    # Verify bot token is set
    if not TOKEN:
        logger.critical("TOKEN environment variable not set. Exiting.")
        sys.exit(1)

    logger.debug(f"Debug mode is {DEBUG}; You can safely ignore this.")

    # Initialize the client
    client = discord.Client(
        token=TOKEN,
        activity=discord.Activity(
            name="Webgroup issues", type=discord.ActivityType.WATCHING
        ),
        auto_defer=True,
        sync_ext=True,
    )

    # Enable built-in extensions
    client.load_extension("interactions.ext.jurigged") # Hot reloading

    # Load custom extensions

    extensions = [Path(f).stem for f in glob.iglob("extensions/[!_]*.py")]

    for extension in extensions:
        try:
            client.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except discord.errors.ExtensionLoadException as e:
            logger.exception(f"Failed to load extension: {extension}", exc_info=e)

    # Start the client

    @discord.listen()
    async def on_startup():
        logger.info(f"Logged in as {client.user}")

    logger.info("Starting client...")
    client.start()