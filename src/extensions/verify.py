import arc
import hikari

from src.config import CHANNEL_IDS, ROLE_IDS, Colour
from src.hooks import restrict_to_channels, restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Verify")


@plugin.include
@arc.with_hook(
    restrict_to_roles(role_ids=[ROLE_IDS["admins"]]),
)
@arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["bot-private"]]))
@arc.slash_command(
    "verify",
    "Verify a Redbrick account.",
)
async def verify_command(
    ctx: BlockbotContext,
    username: arc.Option[
        str,
        arc.StrParams("Redbrick username.", min_length=3, max_length=8),
    ],
    user: arc.Option[
        hikari.User,
        arc.UserParams("The Discord user to verify"),
    ],
) -> None:
    """Verify a Discord member against a Redbrick account."""

    assert ctx.guild_id is not None

    await ctx.client.rest.add_role_to_member(
        ctx.guild_id,
        user,
        ROLE_IDS["brickie"],
        reason="Verified Redbrick user.",
    )

    role = plugin.client.find_command(hikari.CommandType.SLASH, "role add")
    assert isinstance(role, arc.SlashSubCommand)

    await ctx.client.rest.edit_member(
        ctx.guild_id, user, nickname=username, reason="Verified Redbrick user."
    )
    welcome_embed = hikari.Embed(
        description=f"""
        ## Welcome to Redbrick, {user.mention}!
        To get started, type {role.make_mention()} to select your roles and stay up to date with the latest news and events.
        """,
        colour=Colour.BRICKIE_BLUE,
    )
    welcome_embed.set_thumbnail(user.display_avatar_url)

    await plugin.client.rest.create_message(
        CHANNEL_IDS["lobby"],
        content=f"{user.mention} just joined!",
        embed=welcome_embed,
        user_mentions=True,
    )

    admin_embed = hikari.Embed(
        description=f"{user.mention} has been verified with Redbrick username: `{username}`.",
        colour=Colour.BRICKIE_BLUE,
    )

    await ctx.respond(
        embed=admin_embed,
    )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
