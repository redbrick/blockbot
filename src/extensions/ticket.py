import asyncio

import arc
import hikari
from hikari.impl import special_endpoints as se
from hikari.interactions.interaction_components import (
    TextInputInteractionComponent,
    TextSelectMenuInteractionComponent,
)

from src.config import CATEGORY_IDS, ROLE_IDS
from src.hooks import restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin("Ticketing System")


@plugin.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command("create_ticket_message", "Create Ticket Message")
async def options(
    ctx: BlockbotContext,
    channel: arc.Option[
        hikari.TextableChannel,
        arc.ChannelParams("Ticket message channel name"),
    ],
) -> None:
    embed = hikari.Embed(
        title="Tickets",
        description="If you need to contact the admins, helpdesk or committee, create a ticket here!",
    )
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        "meowmeow-create-ticket",
        emoji="✉️",
        label="Create Ticket",
    )
    await ctx.client.rest.create_message(channel, embed=embed, components=[row])
    await ctx.respond("Sent Message")


@plugin.listen()
async def component_interaction(event: hikari.InteractionCreateEvent) -> None:
    if isinstance(event.interaction, hikari.ComponentInteraction):
        if event.interaction.custom_id == "meowmeow-create-ticket":
            await button_click(event.interaction)
        elif event.interaction.custom_id == "honkhonk-close-ticket":
            await close_ticket(event.interaction)
        elif event.interaction.custom_id == "moomoo-close-ticket-confirm":
            await delete_channel(event.interaction)

    elif isinstance(event.interaction, hikari.ModalInteraction):
        if event.interaction.custom_id == "chirpchirp-ticket-channel":
            await modal_submit(event.interaction)


async def button_click(interaction: hikari.ComponentInteraction) -> None:
    text_label = se.LabelComponentBuilder(
        label="Question",
        component=se.TextInputBuilder(
            custom_id="hophop-ticket-question",
            placeholder="Ask your question here!",
            style=hikari.TextInputStyle.PARAGRAPH,
            required=True,
            max_length=1000,
        ),
    )

    committee_select = se.TextSelectMenuBuilder(
        custom_id="ruffruff-committee-select",
        placeholder="Choose Committee Position to Contact",
        min_values=1,
        max_values=1,
    )
    for value in ("admins", "helpdesk", "committee"):
        committee_select.add_option(value.title(), value)
    committee_label = se.LabelComponentBuilder(
        label="Committee", component=committee_select
    )

    await interaction.create_modal_response(
        title="Ticket",
        custom_id="chirpchirp-ticket-channel",
        components=[committee_label, text_label],
    )


async def modal_submit(interaction: hikari.ModalInteraction) -> None:
    committee_choice = interaction.components[0].component
    assert isinstance(committee_choice, TextSelectMenuInteractionComponent)
    selected_committee = committee_choice.values[0]

    question_choice = interaction.components[1].component
    assert isinstance(question_choice, TextInputInteractionComponent)
    selected_question = question_choice.value

    assert interaction.guild_id is not None
    channels = await plugin.client.rest.fetch_guild_channels(interaction.guild_id)
    existing_names = {
        channel.name
        for channel in channels
        if hasattr(channel, "parent_id")
        and channel.parent_id == CATEGORY_IDS["technical"]
    }
    ticket_number = 1
    channel_name = f"ticket-{interaction.user.username}"
    while channel_name in existing_names:
        channel_name = f"ticket-{interaction.user.username}-{ticket_number}"
        ticket_number += 1

    permission_role = ROLE_IDS[selected_committee]
    created_channel = await plugin.client.rest.create_guild_text_channel(
        interaction.guild_id,
        channel_name,
        category=CATEGORY_IDS["technical"],
        permission_overwrites=[
            hikari.PermissionOverwrite(
                id=permission_role,
                type=hikari.PermissionOverwriteType.ROLE,
                allow=hikari.Permissions.VIEW_CHANNEL,
            ),
            hikari.PermissionOverwrite(
                id=interaction.user.id,
                type=hikari.PermissionOverwriteType.MEMBER,
                allow=hikari.Permissions.VIEW_CHANNEL,
            ),
            hikari.PermissionOverwrite(
                id=interaction.guild_id,
                type=hikari.PermissionOverwriteType.ROLE,
                deny=hikari.Permissions.VIEW_CHANNEL,
            ),
        ],
    )

    embed = hikari.Embed(title="Ticket", description=selected_question)
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        "honkhonk-close-ticket",
        emoji="⛔",
        label="Close Ticket",
    )
    await plugin.client.rest.create_message(
        created_channel,
        f"<@&{permission_role}> <@{interaction.user.id}>",
        embed=embed,
        components=[row],
        user_mentions=True,
        role_mentions=True,
    )
    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Ticket Created here: <#{created_channel.id}>!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


async def close_ticket(interaction: hikari.ComponentInteraction) -> None:
    embed = hikari.Embed(
        title="Close Ticket?", description="Are you sure you want to close the ticket?"
    )
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        "moomoo-close-ticket-confirm",
        emoji="⛔",
        label="Close Ticket",
    )
    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        embed=embed,
        components=[row],
        flags=hikari.MessageFlag.EPHEMERAL,
    )


async def delete_channel(interaction: hikari.ComponentInteraction) -> None:
    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        "Closing ticket...",
        flags=hikari.MessageFlag.EPHEMERAL,
    )
    await asyncio.sleep(3)
    await plugin.client.rest.delete_channel(interaction.channel_id)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
