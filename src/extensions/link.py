import re
import secrets
import arc
import hikari
import aiohttp
import time
import asyncio

from src.config import ROLE_IDS, Feature
from src.models import Blockbot, BlockbotContext, BlockbotPlugin
from src.hooks import restrict_to_roles
from src.utils import get_ldap_user_by_discord_id, is_uid_ldap_available, link_discord_to_ldap, get_ldap_user_by_uid

plugin = BlockbotPlugin(name="Link Command Plugin", required_features=[Feature.ADMIN_API])

USERNAME_REGEX = re.compile(r"^[a-z0-9][a-z0-9_]{1,6}[a-z0-9]$")

CODE_EXPIRATION_SECONDS = 300  # Code expires after 5 minutes
PENDING_LINKS: dict[hikari.Snowflake, dict] = {}

async def clean_expired_links() -> None:
    """Periodically purges expired verification sessions to prevent memory leaks."""
    while True:
        try:
            await asyncio.sleep(300) # Run every 5 minutes
            current_time = time.time()

            # Extract expired keys safely
            expired_keys = [
                user_id for user_id, session in PENDING_LINKS.items()
                if current_time > session["expires_at"]
            ]

            for key in expired_keys:
                PENDING_LINKS.pop(key, None)

        except asyncio.CancelledError:
            break
        except Exception:
            pass



@plugin.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["brickie"]]))
@arc.slash_command("link", "Link your Redbrick Account to your Discord")
async def link_command(
        ctx: BlockbotContext,
        username: arc.Option[str, arc.StrParams("Your redbrick username.", min_length=3, max_length=8)],
        code: arc.Option[str | None, arc.StrParams("The 6-digit code sent to your email (if verifying).")] = None,
        aiohttp_client: aiohttp.ClientSession = arc.inject()
) -> None:

    ldap_user = await get_ldap_user_by_discord_id(ctx.author.id, aiohttp_client)
    # Check if the user is already linked
    if ldap_user:
        await ctx.respond("Your account is already linked! If you are experiencing issues, please create a ticket.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    ldap_user = await get_ldap_user_by_uid(username, aiohttp_client)
    # Check if the username is already linked to another Discord account
    if ldap_user and ldap_user.get("user") and ldap_user["user"].get("discord") is not None:
        await ctx.respond("This username is already linked to another Discord account. If you believe this is wrong please create a ticket.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if not USERNAME_REGEX.match(username):
        await ctx.respond("Invalid username. Your username should be 3-8 characters long and only contain letters, numbers, and underscores.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if await is_uid_ldap_available(aiohttp_client, username):
        await ctx.respond("This user doesn't exist. If you believe this is wrong please create a ticket.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    # VERIFICATION MODE (Code provided)
    if code is not None:
        session = PENDING_LINKS.get(ctx.author.id)

        if not session or session["username"] != username:
            await ctx.respond("No active linking session found for this username. Please run `/link` without a code first.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        if time.time() > session["expires_at"]:
            PENDING_LINKS.pop(ctx.author.id, None)  # Clean session safely
            await ctx.respond("Your verification code has expired. Please run `/link` again to get a new one.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        if code != session["code"]:
            await ctx.respond("❌ Invalid verification code. Please try again.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        # SUCCESS: Code matches!
        if not await link_discord_to_ldap(ctx.author.id, username, aiohttp_client):
            await ctx.respond("❌ Failed to link your Discord account. Please try again.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        PENDING_LINKS.pop(ctx.author.id, None)  # Explicitly clear out memory
        await ctx.respond(f"✅ Success! Your Discord account has been successfully linked to Redbrick user `{username}`.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    # No Code provided
    otp_code = f"{secrets.randbelow(1000000):06d}"

    PENDING_LINKS[ctx.author.id] = {
        "username": username,
        "code": otp_code,
        "expires_at": time.time() + CODE_EXPIRATION_SECONDS
    }

    # await send_verification_email(username, otp_code)

    await ctx.respond(
        f"Let's get you linked! A verification code has been generated for `{username}`.\n"
        f"Once you receive it, run `/link username: {username} code: <code>` to complete the process.",
        flags=hikari.MessageFlag.EPHEMERAL
    )

# 5. Loader Setup
@arc.loader
def load(client: Blockbot) -> None:
    client.add_plugin(plugin)
