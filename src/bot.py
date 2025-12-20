import logging

import aiohttp
import arc
import hikari
import miru

from src.config import DEBUG, TOKEN, Feature
from src.database import init_db
from src.models import Blockbot, BlockbotContext

logger = logging.getLogger(__name__)

bot = hikari.GatewayBot(
    token=TOKEN,
    banner=None,
    intents=hikari.Intents.ALL_UNPRIVILEGED
    | hikari.Intents.MESSAGE_CONTENT
    | hikari.Intents.GUILD_MEMBERS,
    logs="DEBUG" if DEBUG else "INFO",
)

client = Blockbot(bot, invocation_contexts=[hikari.ApplicationContextType.GUILD])
miru_client = miru.Client.from_arc(client)

client.set_type_dependency(miru.Client, miru_client)

# log disabled features
for feature in Feature:
    logger.info(f"feature {feature.name} is {'en' if feature.enabled else 'dis'}abled")

client.load_extensions_from("./src/extensions/")
if DEBUG:
    client.load_extensions_from("./src/examples/")

# Misc
if Feature.MISC.enabled:
    client.load_extensions_from("./src/misc/")


@client.listen(hikari.StartingEvent)
async def on_start(_: hikari.StartingEvent) -> None:
    # Create an aiohttp ClientSession to use for web requests
    aiohttp_client = aiohttp.ClientSession()
    client.set_type_dependency(aiohttp.ClientSession, aiohttp_client)


@client.listen(hikari.StoppedEvent)
# By default, dependency injection is only enabled for command callbacks, pre/post hooks & error handlers
# so dependency injection must be enabled manually for this event listener
@client.inject_dependencies
async def on_stop(
    _: hikari.StoppedEvent,
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    await aiohttp_client.close()


@client.set_error_handler
async def error_handler(ctx: BlockbotContext, exc: Exception) -> None:
    if DEBUG:
        message = f"```{exc}```"
    else:
        message = "If this persists, create an issue at <https://webgroup-issues.redbrick.dcu.ie/>."

    # TODO: check double response?
    await ctx.respond(f"❌ Blockbot encountered an unhandled exception. {message}")
    logger.error(exc)

    raise exc


@client.add_startup_hook
async def startup_hook(_: arc.GatewayClient) -> None:
    if Feature.DATABASE.enabled:
        logger.info("Initialising database")
        await init_db()
