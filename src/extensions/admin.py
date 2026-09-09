import arc
import hikari
from hikari.impl import special_endpoints as se

from src.config import ROLE_IDS
from src.hooks import restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Server Admins Commands")


group = plugin.include_slash_group(
    "admin",
    "Redbrick Server Admin Management",
)


# TODO: add other admin messages to this plugin
@group.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_subcommand("create_registration_message", "Create registration message")
async def options(
    ctx: BlockbotContext,
    channel: arc.Option[
        hikari.TextableChannel,
        arc.ChannelParams("Regiestration channel"),
    ],
) -> None:
    embed = hikari.Embed(
        title="Registration",
        description=(
            "**New User**: Provide your information and we'll get you setup with a new Redbrick account.\n"
            "**Existing User:** Already got a Redbrick Account? Provide your username and we'll link it with your Discord account.\n"
            "**Guest**: Join the server temporarily."
        ),
    )
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.SUCCESS,
        "registration-create-new-user-button",
        label="New User",
    )
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        "registration-link-existing-user-button",
        label="Existing User",
    )
    row.add_interactive_button(
        hikari.ButtonStyle.SECONDARY,
        "registration-create-guest-user-button",
        emoji="🔰",
        label="Guest",
    )
    message = await ctx.client.rest.create_message(
        channel, embed=embed, components=[row]
    )
    await ctx.respond(f"Sent message: {message.make_link(ctx.guild_id)}")


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
