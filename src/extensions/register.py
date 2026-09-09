import re

import arc
import hikari
from hikari.impl import special_endpoints as se
from hikari.interactions.interaction_components import (
    TextInputInteractionComponent,
)

from src.config import Feature
from src.models import Blockbot, BlockbotPlugin
from src.utils import (
    is_uid_ldap_available,
)

plugin = BlockbotPlugin("Registration System", required_features=[Feature.ADMIN_API])

USERNAME_REGEX = re.compile(r"^[a-z0-9][a-z0-9_]{1,6}[a-z0-9]$")
STUDENT_ID_REGEX = re.compile(r"[0-9]{5,9}")
COURSE_CODE_REGEX = re.compile(r"^[A-Z]+\d+$")
# allow only DCU emails but not redbrick emails
EMAIL_REGEX = re.compile(r"^[\w\.-]+@(?!redbrick\.)[\w\.-]+\.dcu\.ie$")


@plugin.listen()
async def component_interaction(event: hikari.InteractionCreateEvent) -> None:
    if isinstance(event.interaction, hikari.ComponentInteraction):
        custom_id = event.interaction.custom_id
        if custom_id == "registration-create-new-user-button":
            await new_user_registration_modal(event.interaction)
        elif custom_id == "registration-create-new-user-confirm-button":
            await new_user_registration_confirmation_submit(event.interaction)

    elif isinstance(event.interaction, hikari.ModalInteraction):
        custom_id = event.interaction.custom_id
        if custom_id == "registration-create-new-user-modal":
            await new_user_registration_submit(event.interaction)


async def new_user_registration_modal(interaction: hikari.ComponentInteraction) -> None:
    # josh: swap order to: student id, dcu email, course code, redbrick username
    student_id = se.LabelComponentBuilder(
        label="Student ID",
        description="5-9 digits long. Must not contain letters.",
        component=se.TextInputBuilder(
            custom_id="registration-new-user-student-id",
            placeholder="12345678",
            style=hikari.TextInputStyle.SHORT,
            required=True,
            min_length=5,
            max_length=9,
        ),
    )
    desired_uid = se.LabelComponentBuilder(
        label="Desired Redbrick Username",
        description="3-8 characters long. May only contain letters, numbers, and underscores.",
        component=se.TextInputBuilder(
            custom_id="registration-new-user-desired-uid",
            placeholder="johnrb",
            style=hikari.TextInputStyle.SHORT,
            required=True,
            min_length=3,
            max_length=8,
        ),
    )
    course_code = se.LabelComponentBuilder(
        label="Course Code",
        description="e.g. COMSCI1, ECE1",
        component=se.TextInputBuilder(
            custom_id="registration-new-user-course-code",
            placeholder="COMSCI1",
            style=hikari.TextInputStyle.SHORT,
            required=True,
        ),
    )
    email_address = se.LabelComponentBuilder(
        label="DCU Email Address",
        component=se.TextInputBuilder(
            custom_id="registration-new-user-email-address",
            placeholder="john.redbrick2@mail.dcu.ie",
            style=hikari.TextInputStyle.SHORT,
            required=True,
        ),
    )

    await interaction.create_modal_response(
        title="New User Registration",
        custom_id="registration-create-new-user-modal",
        components=[student_id, desired_uid, course_code, email_address],
    )


async def new_user_registration_submit(interaction: hikari.ModalInteraction) -> None:
    # TODO: helper for this which filters from custom id, could reuse for ticketing
    student_id_choice = interaction.components[0].component
    assert isinstance(student_id_choice, TextInputInteractionComponent)
    student_id = student_id_choice.value.strip()

    desired_uid_choice = interaction.components[1].component
    assert isinstance(desired_uid_choice, TextInputInteractionComponent)
    desired_uid = desired_uid_choice.value.strip().lower()

    course_code_choice = interaction.components[2].component
    assert isinstance(course_code_choice, TextInputInteractionComponent)
    course_code = course_code_choice.value.strip().upper()

    email_address_choice = interaction.components[3].component
    assert isinstance(email_address_choice, TextInputInteractionComponent)
    email_address = email_address_choice.value.strip().lower()

    error_message: str | None = None

    if not STUDENT_ID_REGEX.match(student_id):
        error_message = "Invalid student ID: must be an integer 5-9 digits long and not contain letters."
    elif not USERNAME_REGEX.match(desired_uid):
        error_message = (
            "Invalid username: must be 3-8 characters long and only contains letters, numbers, and "
            "underscores, and must not start or end with an underscore."
        )
    elif not COURSE_CODE_REGEX.match(course_code):
        error_message = (
            "Invalid course code: must be a valid code like `COMSCI1` or `ECE1`."
        )
    elif not EMAIL_REGEX.match(email_address):
        error_message = (
            "Invalid email format. Please make sure it's a DCU email address."
        )
    elif not await is_uid_ldap_available(desired_uid):
        error_message = (
            f"The username `{desired_uid}` is already taken. Please try another one."
        )

    if error_message is not None:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            error_message,
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    message = f"""
## {interaction.user.mention}, your registration details are:
- Student ID: `{student_id}`
- Desired Redbrick username: `{desired_uid}`
- Course code: `{course_code}`
- DCU Email: `{email_address}`

Please confirm these details are correct and press the button below to submit your registration.
    """
    embed = hikari.Embed(description=message)
    row = se.MessageActionRowBuilder()
    row.add_interactive_button(
        hikari.ButtonStyle.SUCCESS,
        "registration-create-new-user-confirm-button",
        label="Confirm",
    )
    row.add_interactive_button(
        hikari.ButtonStyle.DANGER,
        "registration-create-new-user-cancel-button",
        label="Cancel Registration",
    )

    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        embed=embed,
        flags=hikari.MessageFlag.EPHEMERAL,
        components=[row],
    )


async def new_user_registration_confirmation_submit(
    interaction: hikari.ComponentInteraction,
) -> None:
    pass


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
