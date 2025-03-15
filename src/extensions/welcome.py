import arc
import hikari

from src.config import CHANNEL_IDS
from src.utils import channel_mention, get_guild

plugin = arc.GatewayPlugin(name="Welcome")


@plugin.listen()
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.message.type != hikari.MessageType.GUILD_MEMBER_JOIN:
        return

    assert event.member is not None
    guild_name = await get_guild(plugin.client, event)
    message = f"""
# Welcome to {guild_name}!

- Have a read of the {channel_mention(CHANNEL_IDS["rules"])} and {channel_mention(CHANNEL_IDS["instructions"])} to get started.
- If you don't have a {guild_name} account yet, please type `/register` to create a new account.
- Once you have a {guild_name} account, verify your account by typing `/verify` in this channel.

### *Stuck?* Check out {channel_mention(CHANNEL_IDS["instructions"])} or ask for help in this channel.
"""
    embed = hikari.Embed(description=message)
    embed.set_thumbnail(event.member.avatar_url)

    await plugin.client.rest.create_message(
        CHANNEL_IDS["waiting-room"],
        user_mentions=True,
        content=f"{event.member.mention}",
        embed=embed,
    )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
