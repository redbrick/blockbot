import arc
import hikari

from src.config import CHANNEL_IDS
from src.utils import channel_mention, get_guild

plugin = arc.GatewayPlugin(name="Welcome")


@plugin.listen()
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    guild = await get_guild(plugin.client, event)

    # TODO: use built-in arc command finder once it's released
    register = plugin.client._slash_commands["register"]  # pyright: ignore[reportPrivateUsage]
    assert isinstance(register, arc.SlashCommand)

    message = f"""
# Welcome to {guild.name}!

- Have a read of the {channel_mention(CHANNEL_IDS["rules"])} and {channel_mention(CHANNEL_IDS["instructions"])} to get started.
- If you don't have a {guild.name} account yet, please type {register.make_mention()} to create a new account.

### *Stuck?* Check out {channel_mention(CHANNEL_IDS["instructions"])} or ask for help in this channel.
"""
    embed = hikari.Embed(description=message)
    embed.set_thumbnail(event.member.display_avatar_url)

    await plugin.client.rest.create_message(
        CHANNEL_IDS["waiting-room"],
        user_mentions=True,
        content=f"{event.member.mention}",
        embed=embed,
    )


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
