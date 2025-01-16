from __future__ import annotations

import enum
import logging

import arc
import hikari
from sqlalchemy import insert, select, update

from src.database import Session, Starboard, StarboardSettings

logger = logging.getLogger(__name__)

plugin = arc.GatewayPlugin("Starboard")


class StarboardSettingsError(enum.IntEnum):
    CHANNEL_FORBIDDEN = 0
    CHANNEL_NOT_FOUND = 1


# TODO: handle star remove
@plugin.listen()
async def on_reaction(
    event: hikari.GuildReactionAddEvent,
) -> None:
    logger.info("Received guild reaction add event")

    if event.emoji_name != "⭐":
        return

    message = await plugin.client.rest.fetch_message(event.channel_id, event.message_id)
    star_count = sum(r.emoji == "⭐" for r in message.reactions)

    # get starboard settings
    async with Session() as session:
        stmt = select(StarboardSettings).where(
            StarboardSettings.guild_id == event.guild_id
        )
        result = await session.execute(stmt)
        settings = result.scalars().first()

    # TODO: remove temporary logging and merge into one if statement
    if not settings:
        logger.info("Received star but no guild starboard set")
        return
    if star_count < settings.threshold:
        logger.info("Not enough stars to post to starboard")
        return
    if not settings.channel_id:
        logger.info("No starboard channel set")
        return
    if settings.error is not None:
        logger.info("Error with starboard channel")
        return

    # TODO: consider ignoring stars reacted to a starboard message

    # get starred message
    async with Session() as session:
        stmt = select(Starboard).where(Starboard.message_id == event.message_id)
        result = await session.execute(stmt)
        starboard = result.scalars().first()

    embed = hikari.Embed(
        title=f"⭐ {star_count} - *jump to message*",
        url=message.make_link(event.guild_id),
        description=message.content,
        timestamp=message.timestamp,
    ).set_author(
        name=message.author.username,
        icon=message.author.display_avatar_url,
    )

    images = [
        att
        for att in message.attachments
        if att.media_type and att.media_type.startswith("image")
    ]
    if images:
        embed.set_image(images[0])

    embeds = [embed, *message.embeds]

    try:
        if not starboard:
            logger.info("Creating message")
            message = await plugin.client.rest.create_message(
                settings.channel_id,
                embeds=embeds,
            )

            async with Session() as session:
                session.add(
                    Starboard(
                        channel_id=event.channel_id,
                        message_id=event.message_id,
                        stars=star_count,
                        starboard_channel_id=settings.channel_id,
                        starboard_message_id=message.id,
                    )
                )
                await session.commit()
        else:
            try:
                logger.info("Editing message")
                await plugin.client.rest.edit_message(
                    starboard.starboard_channel_id,
                    starboard.starboard_message_id,
                    embeds=embeds,
                )
            except hikari.NotFoundError:
                logger.info("Starboard message does not exist, creating new")
                message = await plugin.client.rest.create_message(
                    settings.channel_id,
                    embeds=embeds,
                )
                async with Session() as session:
                    stmt = (
                        update(Starboard)
                        .where(
                            Starboard.starboard_message_id
                            == starboard.starboard_message_id
                        )
                        .values(
                            starboard_message_id=message.id,
                        )
                    )
                    await session.execute(stmt)
                    await session.commit()

    except hikari.ForbiddenError:
        logger.info("Can't access starboard channel")

        async with Session() as session:
            stmt = (
                update(StarboardSettings)
                .where(StarboardSettings.guild_id == event.guild_id)
                .values(error=StarboardSettingsError.CHANNEL_FORBIDDEN)
            )
            await session.execute(stmt)
            await session.commit()
    except hikari.NotFoundError:
        logger.info("Can't find starboard channel")

        async with Session() as session:
            stmt = (
                update(StarboardSettings)
                .where(StarboardSettings.guild_id == event.guild_id)
                .values(error=StarboardSettingsError.CHANNEL_NOT_FOUND)
            )
            await session.execute(stmt)
            await session.commit()


# TODO: add permission hook
@plugin.include
@arc.slash_command(
    "starboard",
    "Edit or view starboard settings.",
    default_permissions=hikari.Permissions.MANAGE_GUILD,
)
async def starboard_settings(
    ctx: arc.GatewayContext,
    channel: arc.Option[
        hikari.TextableGuildChannel | None,
        arc.ChannelParams("The channel to post starboard messages to."),
    ] = None,
    threshold: arc.Option[
        int | None,
        arc.IntParams(
            "The minimum number of stars before this message is posted to the starboard",
            min=1,
        ),
    ] = None,
) -> None:
    assert ctx.guild_id

    async with Session() as session:
        stmt = select(StarboardSettings).where(
            StarboardSettings.guild_id == ctx.guild_id
        )
        result = await session.execute(stmt)
        settings = result.scalars().first()

    if not channel and not threshold:
        if not settings:
            await ctx.respond(
                "This server has no starboard settings.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            # TODO: `channel` and `threshold` can be None
            embed = hikari.Embed(
                title="Starboard Settings",
                description=(
                    f"**Channel:** <#{settings.channel_id}>\n"
                    f"**Threshold:** {settings.threshold}\n"
                    + (f"**Error:** {settings.error}" if settings.error else "")
                ),
            )
            await ctx.respond(embed)

        return

    # TODO: use returning statement to get back new row
    # then send embed

    if not settings:
        # TODO: use add not insert
        stmt = insert(StarboardSettings).values(guild_id=ctx.guild_id)
    else:
        stmt = update(StarboardSettings).where(
            StarboardSettings.guild_id == ctx.guild_id
        )

    # TODO: simplify logic
    if channel and threshold:
        stmt = stmt.values(channel_id=channel.id, threshold=threshold)
    elif channel:
        stmt = stmt.values(channel_id=channel.id)
    elif threshold:
        stmt = stmt.values(threshold=threshold)

    async with Session() as session:
        await session.execute(stmt)
        await session.commit()

    await ctx.respond("Settings updated.", flags=hikari.MessageFlag.EPHEMERAL)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
