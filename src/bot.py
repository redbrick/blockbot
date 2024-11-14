import logging
import sys

import arc
import hikari
import aiohttp
import miru

from src.config import DEBUG, TOKEN, LDAP_USERNAME, LDAP_PASSWORD

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
miru_client = miru.Client.from_arc(client)

client.set_type_dependency(miru.Client, miru_client)

client.load_extensions_from("./src/extensions/")

if DEBUG:
    client.load_extensions_from("./src/examples/")


@client.listen(hikari.StartingEvent)
async def on_start(event: hikari.StartingEvent) -> None:
    # Create an aiohttp ClientSession to use for web requests
    aiohttp_client = aiohttp.ClientSession()
    client.set_type_dependency(aiohttp.ClientSession, aiohttp_client)

    await hedgedoc_login(aiohttp_client)

@client.listen(hikari.StoppedEvent)
# By default, dependency injection is only enabled for command callbacks, pre/post hooks & error handlers
# so dependency injection must be enabled manually for this event listener
@client.inject_dependencies 
async def on_stop(event: hikari.StoppedEvent, aiohttp_client: aiohttp.ClientSession = arc.inject()) -> None:
    await aiohttp_client.close()

async def hedgedoc_login(aiohttp_client: aiohttp.ClientSession) -> None:
    data = {
        "username": LDAP_USERNAME,
        "password": LDAP_PASSWORD,
    }

    response = await aiohttp_client.post(
        "https://md.redbrick.dcu.ie/auth/ldap", data=data
    )
    if response.ok:
        logging.info("Login to MD successful!")
    else:
        # Ideally need a retry system
        logging.info("Login to MD failed!")


@client.set_error_handler
async def error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    if DEBUG:
        message = f"```{exc}```"
    else:
        message = "If this persists, create an issue at <https://webgroup-issues.redbrick.dcu.ie/>."

    await ctx.respond(f"❌ Blockbot encountered an unhandled exception. {message}")
    logging.error(exc)

    raise exc
