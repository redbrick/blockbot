import arc
import hikari
import requests
import re

# not used, functionality for times/deadlines to be added later
from datetime import datetime, timezone

from src.utils import role_mention
from src.hooks import restrict_to_channels, restrict_to_roles
from src.config import CHANNEL_IDS, ROLE_IDS, UID_MAPS, LDAP_USERNAME, LDAP_PASSWORD


action_items = arc.GatewayPlugin(name="Action Items")

session = requests.Session()

data = {
    "username": LDAP_USERNAME,
    "password": LDAP_PASSWORD,
}

response = session.post("https://md.redbrick.dcu.ie/auth/ldap", data=data)
if response.ok:
    print("Login to MD successful!")
else:
    print("Login to MD failed!")


@action_items.include
# @arc.with_hook(restrict_to_channels(channel_ids=[CHANNEL_IDS["action-items"]]))
# @arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command("action_items", "Display the action items from the MD")
async def get_action_items(
    ctx: arc.GatewayContext,
    url: arc.Option[str, arc.StrParams("URL of the minutes from the MD")],
) -> None:
    """Display the action items from the MD!"""

    if "https://md.redbrick.dcu.ie" not in url:
        await ctx.respond(
            f"❌ `{url}` is not a valid MD URL. Please provide a valid URL.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    url_without_fragment = url.split("#", 1)[0]

    clean_url = url_without_fragment.split("?", 1)[0]

    request = clean_url + "/download"
    response = session.get(request)
    if not response.status_code == 200:
        await ctx.respond(
            f"❌ Failed to fetch the minutes. Status code: `{response.status_code}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    content = response.text

    action_items_section = re.search(
        r"# Action Items:?\n(.*?)(\n# |\n---|$)", content, re.DOTALL
    )

    if not action_items_section:
        await ctx.respond("❌ No `Action Items` section found.")
        return

    # Get the matched content (excluding the "Action Items" heading itself)
    action_items_content = action_items_section.group(1)

    bullet_points = re.findall(r"^\s*[-*]\s+(.+)", action_items_content, re.MULTILINE)
    formatted_bullet_points = [
        "- " + re.sub(r"^\[.\]\s+", "", item) for item in bullet_points
    ]

    # Replace user names with user mentions
    for i, item in enumerate(formatted_bullet_points):
        for name, uid in UID_MAPS.items():
            item = item.replace(f"`{name}`", f"<@{uid}>")
        formatted_bullet_points[i] = item

    # Replace role names with role mentions
    for i, item in enumerate(formatted_bullet_points):
        for role, role_id in ROLE_IDS.items():
            item = item.replace(f"`{role}`", role_mention(role_id))
        formatted_bullet_points[i] = item

    # Send title to the action-items channel
    await action_items.client.rest.create_message(
        CHANNEL_IDS["action-items"], content="# Action Items:"
    )

    # send each bullet point seperately
    for item in formatted_bullet_points:
        await action_items.client.rest.create_message(
            CHANNEL_IDS["action-items"], content=item
        )
    # respond with success if it executes successfully
    await ctx.respond("✅ Action Items sent successfully!")
    return


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(action_items)
