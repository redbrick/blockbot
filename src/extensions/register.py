import contextlib
import json
import re

import arc
import hikari
import miru

from src.config import CHANNEL_IDS, ROLE_IDS
from src.hooks import restrict_to_channels
from src.utils import role_mention

plugin = arc.GatewayPlugin(name="Register")

USERNAME_REGEX = re.compile(r"^[a-z0-9][a-z0-9_]{1,6}[a-z0-9]$")
STUDENT_ID_REGEX = re.compile(r"[0-9]{5,9}")
COURSE_CODE_REGEX = re.compile(r"^[A-Z]+\d+$")
MAIL_REGEX = re.compile(
    r"^[\w\.-]+@(?!redbrick\.)[\w\.-]+\.dcu\.ie$"
)  # allow only DCU emails but not redbrick emails


class RegisterView(miru.View):
    def __init__(
        self,
        user_id: int,
        student_id: str,
        desired_uid: str,
        mod_code: str,
        mail: str,
    ) -> None:
        self.user_id = user_id
        self.student_id = student_id
        self.desired_uid = desired_uid
        self.mod_code = mod_code
        self.mail = mail
        super().__init__(timeout=60)

    async def stop_view(self) -> None:
        for item in self.children:
            item.disabled = True

        # the view is bound to the /register command response
        assert self.message is not None
        # the user may have dismissed the ephemeral response already
        with contextlib.suppress(hikari.NotFoundError):
            await self.message.edit(components=self)

        return super().stop()

    async def on_timeout(self) -> None:
        await self.stop_view()

    @miru.button(
        emoji="✅", label="Confirm Registration", custom_id="confirm_registration"
    )
    async def click_button(self, ctx: miru.ViewContext, _: miru.Button) -> None:
        if ctx.user.id != self.user_id:
            await ctx.respond(
                "You are not allowed to confirm this registration.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        user_data = {
            "student_id": self.student_id,
            "desired_uid": self.desired_uid,
            "mod_code": self.mod_code,
            "mail": self.mail,
        }

        admin_message = f"""
{role_mention(ROLE_IDS["admins"])}
## {ctx.user.mention}'s registration details are:
- Student ID: `{self.student_id}`
- Desired Username: `{self.desired_uid}`
- Course Code: `{self.mod_code}`
- Email: `{self.mail}`
### JSON:
```json
{json.dumps(user_data)}
```
        """
        await plugin.client.rest.create_message(
            CHANNEL_IDS["bot-private"], content=admin_message, role_mentions=True
        )

        await ctx.edit_response(
            "Your registration has been confirmed. Thank you!",
            embed=None,
            components=[],
        )

        await self.stop_view()


@plugin.include
@arc.with_hook(
    restrict_to_channels(
        channel_ids=[
            CHANNEL_IDS["waiting-room"],
        ],
    ),
)
@arc.slash_command(
    "register",
    "Create a Redbrick account.",
    autodefer=arc.AutodeferMode.EPHEMERAL,  # ensure all responses are ephemeral if auto defer responds first
)
async def register_command(
    ctx: arc.GatewayContext,
    student_id: arc.Option[
        str, arc.StrParams(description="Your student ID.", min_length=5, max_length=9)
    ],
    desired_uid: arc.Option[
        str,
        arc.StrParams("Your desired Redbrick username.", min_length=3, max_length=8),
    ],
    mod_code: arc.Option[str, arc.StrParams("Your course code. (e.g. COMSCI1, ECE1)")],
    mail: arc.Option[str, arc.StrParams("Your DCU email address.")],
    miru_client: miru.Client = arc.inject(),
) -> None:
    """Register a Redbrick account."""

    student_id = student_id.strip()
    desired_uid = desired_uid.strip().lower()
    mod_code = mod_code.strip().upper()
    mail = mail.strip().lower()

    error_message: str | None = None

    if not STUDENT_ID_REGEX.match(student_id):
        error_message = "Invalid student ID format. `student_id` must be an integer between 5 and 9 digits long and must not contain letters."
    elif not USERNAME_REGEX.match(desired_uid):
        error_message = "Invalid username. Please ensure the desired username is 3-8 characters long and only contains letters, numbers, and underscores."
    elif not COURSE_CODE_REGEX.match(mod_code):
        error_message = "Invalid course code format. Please provide a valid code like `COMSCI1` or `ECE1`."
    elif not MAIL_REGEX.match(mail):
        error_message = (
            "Invalid email format. Please make sure it's a DCU email address."
        )

    if error_message is not None:
        await ctx.respond(error_message, flags=hikari.MessageFlag.EPHEMERAL)
        return

    message = f"""
## {ctx.user.mention}, your registration details are:
- Student ID: `{student_id}`
- Desired Username: `{desired_uid}`
- Course Code: `{mod_code}`
- Email: `{mail}`

**Please confirm these details are correct and press the button below to submit your registration.**
"""

    embed = hikari.Embed(
        description=message,
    )
    view = RegisterView(ctx.user.id, student_id, desired_uid, mod_code, mail)
    response = await ctx.respond(
        embed=embed,
        flags=hikari.MessageFlag.EPHEMERAL,
        user_mentions=True,
        components=view,
    )

    miru_client.start_view(view, bind_to=await response.retrieve_message())


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
