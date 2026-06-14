import arc
import hikari
from hikari.impl import special_endpoints as se
from hikari.interactions.interaction_components import (
    TextInputInteractionComponent,
    TextSelectMenuInteractionComponent,
)

from src.config import CATEGORY_IDS, ROLE_IDS
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin("Ticketing System")


@plugin.include
@arc.slash_command("create_ticket_message", "Create Ticket Message")
async def options(
    ctx: BlockbotContext,
    channel_option: arc.Option[
        hikari.TextableChannel,
        arc.ChannelParams("A textable channel option.", name="channel"),
    ],
) -> None:
    embed = hikari.Embed(title="Tickets", description="Create a ticket here!")
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, "meowmeow1", emoji="✉️", label="Create Ticket"
    )
    await ctx.client.rest.create_message(channel_option, embed=embed, components=[row])
    await ctx.respond("Sent Message")


@plugin.listen()
async def button_click(event: hikari.InteractionCreateEvent) -> None:
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if event.interaction.custom_id != "meowmeow1":
        return

    text_label = se.LabelComponentBuilder(
        label="Question",
        component=se.TextInputBuilder(
            custom_id="hophop1",
            style=hikari.TextInputStyle.PARAGRAPH,
            required=True,
            max_length=1000,
        ),
    )

    committee_select = se.TextSelectMenuBuilder(
        custom_id="ruffruff1",
        placeholder="Choose Committee Position",
        min_values=1,
        max_values=1,
    )
    for value in ("admins", "helpdesk", "committee"):
        committee_select.add_option(value.title(), value)
    committee_label = se.LabelComponentBuilder(
        label="Committee", component=committee_select
    )

    await event.interaction.create_modal_response(
        title="Ticket",
        custom_id="chirpchirp1",
        components=[committee_label, text_label],
    )


@plugin.listen()
async def modal_submit(event: hikari.InteractionCreateEvent) -> None:
    if not isinstance(event.interaction, hikari.ModalInteraction):
        return
    if event.interaction.custom_id != "chirpchirp1":
        return

    committee_choice = event.interaction.components[0].component
    assert isinstance(committee_choice, TextSelectMenuInteractionComponent)
    selected_committee = committee_choice.values[0]

    question_choice = event.interaction.components[1].component
    assert isinstance(question_choice, TextInputInteractionComponent)
    selected_question = question_choice.value

    # TODO: Make channel name work with multiple tickets per user
    channel_name = f"ticket-{event.interaction.user.username}"
    assert event.interaction.guild_id is not None
    permission_role = ROLE_IDS[selected_committee]
    created_channel = await event.app.rest.create_guild_text_channel(
        event.interaction.guild_id,
        channel_name,
        category=CATEGORY_IDS["test-category"],
        permission_overwrites=[
            hikari.PermissionOverwrite(
                id=permission_role,
                type=hikari.PermissionOverwriteType.ROLE,
                allow=hikari.Permissions.VIEW_CHANNEL,
            ),
            hikari.PermissionOverwrite(
                id=event.interaction.user.id,
                type=hikari.PermissionOverwriteType.MEMBER,
                allow=hikari.Permissions.VIEW_CHANNEL,
            ),
            hikari.PermissionOverwrite(
                id=event.interaction.guild_id,
                type=hikari.PermissionOverwriteType.ROLE,
                deny=hikari.Permissions.VIEW_CHANNEL,
            ),
        ],
    )

    embed = hikari.Embed(title="Ticket", description=selected_question)
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, "honkhonk1", emoji="⛔", label="Close Ticket"
    )
    await event.app.rest.create_message(created_channel, embed=embed, components=[row])
    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Ticket Created here: <#{created_channel.id}>!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
