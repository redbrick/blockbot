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
    assert ctx.member is not None
    if ROLE_IDS["admins"] not in ctx.member.role_ids:
        await ctx.respond("You don't have permission to use this command!", flags=hikari.MessageFlag.EPHEMERAL)
        return
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

    assert event.interaction.guild_id is not None
    channels = await event.app.rest.fetch_guild_channels(event.interaction.guild_id)
    existing_names = {
        channel.name
        for channel in channels
        if hasattr(channel, "parent_id")
        and channel.parent_id == CATEGORY_IDS["technical"]
    }
    ticket_number = 1
    channel_name = f"ticket-{event.interaction.user.username}"
    while channel_name in existing_names:
        channel_name = f"ticket-{event.interaction.user.username}-{ticket_number}"
        ticket_number += 1

    permission_role = ROLE_IDS[selected_committee]
    created_channel = await event.app.rest.create_guild_text_channel(
        event.interaction.guild_id,
        channel_name,
        category=CATEGORY_IDS["technical"],
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
    await event.app.rest.create_message(
        created_channel.id, f"<@&{permission_role}> <@{event.interaction.user.id}>"
    )


@plugin.listen()
async def close_ticket(event: hikari.InteractionCreateEvent) -> None:
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if event.interaction.custom_id != "honkhonk1":
        return

    embed = hikari.Embed(
        title="Close Ticket?", description="Are you sure you want to close the ticket?"
    )
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, "moomoo1", emoji="⛔", label="Close Ticket"
    )
    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        embed=embed,
        components=[row],
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.listen()
async def delete_channel(event: hikari.InteractionCreateEvent) -> None:
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if event.interaction.custom_id != "moomoo1":
        return

    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        "Closing ticket...",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await event.app.rest.delete_channel(event.interaction.channel_id)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
