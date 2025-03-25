import arc
import hikari
import miru

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin("Example Modal")


# Modals Guide: https://miru.hypergonial.com/guides/modals/
class MyModal(miru.Modal, title="Tell us about yourself!"):
    name = miru.TextInput(
        label="Name",
        placeholder="Enter your name!",
        required=True,
    )

    bio = miru.TextInput(
        label="Biography",
        value="Age: \nHobbies:",  # pre-filled content
        style=hikari.TextInputStyle.PARAGRAPH,
        required=False,
    )

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # values can also be accessed using ctx.values,
        # Modal.values, or with ctx.get_value_by_id()
        embed = hikari.Embed(title=self.name.value, description=self.bio.value)
        await ctx.respond(embed=embed)


@plugin.include
@arc.slash_command("modal", "A command with a modal response.")
async def modal_command(
    ctx: BlockbotContext,
    miru_client: miru.Client = arc.inject(),
) -> None:
    modal = MyModal()
    builder = modal.build_response(miru_client)

    # arc has a built-in way to respond with a builder
    await ctx.respond_with_builder(builder)

    miru_client.start_modal(modal)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
