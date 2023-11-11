"""
Main script to run

This script initializes extensions and starts the bot
"""
import os
import sys
from interactions import Activity, ActivityType, Client, listen, errors
from config import DEBUG, DEV_GUILD, TOKEN
import logutil

# Configure logging for this main.py handler
logger = logutil.init_logger("main.py")
logger.debug("Debug mode is %s; You can safely ignore this.", DEBUG)

# Check if TOKEN is set
if not TOKEN:
    logger.critical("TOKEN variable not set. Cannot continue")
    sys.exit(1)

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

# Register a listener for the startup event
@listen()
async def on_startup():
    """Called when the bot starts"""
    logger.info(f"Logged in as {client.user}")

# Load built-in extensions
client.load_extension("interactions.ext.jurigged")

# Load all python files in "extensions" folder
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
        logger.exception(f"Failed to load extension: {extension}.", exc_info=e)

# Start the client
client.start()
