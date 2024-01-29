import arc
import hikari

from src.config import CHANNEL_IDS

plugin = arc.GatewayPlugin(name="Boosts")

TIER_COUNT: dict[hikari.MessageType, None | int] = {
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION: None,
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1: 1,
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: 2,
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: 3,
}


# NOTE: this is baked into discord-interactions-py, so I extracted and cleaned up the logic
def get_boost_message(
    message_type: hikari.MessageType | int, content: str | None, author: hikari.Member, guild: hikari.Guild
) -> str:
    assert message_type in (
        hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION,
        hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1,
        hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2,
        hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3,
    )

    message = f"{author.display_name} just boosted the server{f' **{content}** times' if content else ''}!"

    if (count := TIER_COUNT[message_type]) is not None:
        message += f"{guild.name} has achieved **Level {count}!**"

    return message


@plugin.listen()
async def on_message(event: hikari.GuildMessageCreateEvent):
    if event.message.type in TIER_COUNT:
        assert event.member is not None
        message = get_boost_message(
            event.message.type,
            event.content,
            event.member,
            event.get_guild() or await plugin.client.rest.fetch_guild(event.guild_id),
        )
        await plugin.client.rest.create_message(CHANNEL_IDS["lobby"], content=message)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)