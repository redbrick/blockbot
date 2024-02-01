import arc
import hikari

from src.config import CHANNEL_IDS
from src.utils import get_guild

plugin = arc.GatewayPlugin(name="Boosts")

BOOST_TIERS: list[hikari.MessageType] = [
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1,
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2,
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3,
]

BOOST_MESSAGE_TYPES: list[hikari.MessageType] = BOOST_TIERS + [
    hikari.MessageType.USER_PREMIUM_GUILD_SUBSCRIPTION,
]

def build_boost_message(
    message_type: hikari.MessageType | int,
    number_of_boosts: str | None,
    booster_user: hikari.Member,
    guild: hikari.Guild
) -> str:
    assert message_type in BOOST_MESSAGE_TYPES

    base_message = f"{booster_user.display_name} just boosted the server"
    multiple_boosts_message = f" **{number_of_boosts}** times" if number_of_boosts else ""

    message = base_message + multiple_boosts_message + "!"

    if (message_type in BOOST_TIERS):
        count = BOOST_TIERS.index(message_type)
        message += f"\n{guild.name} has reached **Level {count}!**"

    return message

@plugin.listen()
async def on_message(event: hikari.GuildMessageCreateEvent):
    if not event.message.type in BOOST_MESSAGE_TYPES:
        return

    assert event.member is not None
    message = build_boost_message(
        event.message.type,
        number_of_boosts=event.content,
        booster_user=event.member,
        guild=await get_guild(plugin.client, event)
    )

    await plugin.client.rest.create_message(CHANNEL_IDS["lobby"], content=message)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
