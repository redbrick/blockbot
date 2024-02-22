from __future__ import annotations

import logging

import arc
import hikari
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database import Starboard, StarboardSettings

logger = logging.getLogger(__name__)

plugin = arc.GatewayPlugin("Starboard")

@plugin.listen()
@plugin.inject_dependencies
async def on_reaction(
    event: hikari.GuildReactionAddEvent,
    session: AsyncEngine = arc.inject(),
) -> None:
    logger.info("Received guild reaction add event")
    
    if event.emoji_name != "⭐":
        return

    message = await plugin.client.rest.fetch_message(event.channel_id, event.message_id)
    star_count = sum(r.emoji == "⭐" for r in message.reactions)

    stmt = select(StarboardSettings).where(StarboardSettings.guild == event.guild_id)
    async with session.connect() as conn:
        result = await conn.execute(stmt)

    settings = result.first()

    # TODO: remove temporary logging and merge into one if statement
    if not settings:
        logger.info("Received star but no guild starboard set")
        return
    if star_count < settings.threshold:
        logger.info("Not enough stars to post to starboard")
        return
    if not settings.channel:
        logger.info("No starboard channel set")
        return
    
    async with session.connect() as conn:
        stmt = select(Starboard).where(Starboard.message == event.message_id)
        result = await conn.execute(stmt)
        starboard = result.first()

        logger.info(starboard)
        
        if not starboard:
            stmt = select(Starboard).where(Starboard.starboard_message == event.message_id)
            result = await conn.execute(stmt)
            starboard = result.first()

        logger.info(starboard)

    embed = hikari.Embed(description=f"⭐ {star_count}\n[link]({message.make_link(event.guild_id)})")

    # TODO: handle starring the starboard message
    # i.e. don't create a starboard message for the starboard message

    if not starboard:
        try:
            logger.info("Creating message")
            message = await plugin.client.rest.create_message(
                settings.channel,
                embed,
            )
            stmt = insert(Starboard).values(
                channel=event.channel_id,
                message=event.message_id,
                stars=star_count,
                starboard_channel=settings.channel,
                starboard_message=message.id,
                starboard_stars=0,
            )

            async with session.begin() as conn:
                await conn.execute(stmt)
                await conn.commit()
        except hikari.ForbiddenError:
            logger.info("Can't access starboard channel")
            stmt = update(StarboardSettings).where(StarboardSettings.guild == event.guild_id).values(
                channel=None)

            async with session.begin() as conn:
                await conn.execute(stmt)
                await conn.commit()

    else:
        try:
            logger.info("Editing message")
            await plugin.client.rest.edit_message(
                starboard.starboard_channel,
                starboard.starboard_message,
                embed
            )
        except hikari.ForbiddenError:
            logger.info("Can't edit starboard message")
            stmt = delete(StarboardSettings).where(StarboardSettings.guild == event.guild_id)

            async with session.begin() as conn:
                await conn.execute(stmt)
                await conn.commit()

@plugin.include
@arc.slash_command("starboard", "Edit or view starboard settings.", default_permissions=hikari.Permissions.MANAGE_GUILD)
async def starboard_settings(
    ctx: arc.GatewayContext,
    channel: arc.Option[hikari.TextableGuildChannel | None, arc.ChannelParams("The channel to post starboard messages to.")] = None,
    threshold: arc.Option[int | None, arc.IntParams("The minimum number of stars before this message is posted to the starboard", min=1)] = None,
    session: AsyncEngine = arc.inject(),
) -> None:
    assert ctx.guild_id

    stmt = select(StarboardSettings).where(StarboardSettings.guild == ctx.guild_id)
    async with session.connect() as conn:
        result = await conn.execute(stmt)

    settings = result.first()

    if not channel and not threshold:
        if not settings:
            await ctx.respond("This server has no starboard settings.", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            # TODO: `channel` and `threshold` can be None
            embed = hikari.Embed(
                title="Starboard Settings",
                description=(
                    f"**Channel:** <#{settings.channel}>\n"
                    f"**Threshold:** {settings.threshold}"
                ),
            )
            await ctx.respond(embed)
            
        return
    
    if not settings:
        stmt = insert(StarboardSettings).values(guild=ctx.guild_id)
    else:
        stmt = update(StarboardSettings).where(StarboardSettings.guild == ctx.guild_id)

    # TODO: simplify logic
    if channel and threshold:
        stmt = stmt.values(channel=channel.id, threshold=threshold)
    elif channel:
        stmt = stmt.values(channel=channel.id)
    elif threshold:
        stmt = stmt.values(threshold=threshold)

    async with session.begin() as conn:
        await conn.execute(stmt)
        await conn.commit()
    
    # TODO: respond with embed of new settings?
    await ctx.respond("Settings updated.", flags=hikari.MessageFlag.EPHEMERAL)

@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
