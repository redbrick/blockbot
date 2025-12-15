import arc
import hikari

from src.config import CHANNEL_IDS, DEFAULT_ROLES, ROLE_IDS, Colour
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
    member: arc.Option[
        hikari.Member,
        arc.MemberParams("The member to verify."),
    ],
) -> None:
    """Verify a Discord member against a Redbrick account."""

    assert ctx.guild_id is not None

    final_role_ids = list(set(member.role_ids) | DEFAULT_ROLES)

    await ctx.client.rest.edit_member(
        ctx.guild_id,
        member,
        nickname=username,
        roles=final_role_ids,
        reason="Verified Redbrick user.",
    )

    role = plugin.client.find_command(hikari.CommandType.SLASH, "role add")
    assert isinstance(role, arc.SlashSubCommand)

    welcome_embed = hikari.Embed(
        description=f"""
        ## Welcome to Redbrick, {member.mention}!
        To get started, type {role.make_mention()} to select your roles and stay up to date with the latest news and events.
        """,
        colour=Colour.BRICKIE_BLUE,
    )
    welcome_embed.set_thumbnail(member.display_avatar_url)

    await plugin.client.rest.create_message(
        CHANNEL_IDS["lobby"],
        content=f"{member.mention} just joined!",
        embed=welcome_embed,
        user_mentions=True,
    )

    admin_embed = hikari.Embed(
        description=f"{member.mention} has been verified with Redbrick username: `{username}`.",
        colour=Colour.BRICKIE_BLUE,
    )

    await ctx.respond(
        embed=admin_embed,
    )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
