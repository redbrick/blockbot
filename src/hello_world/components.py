import arc
import hikari
import miru

plugin = arc.GatewayPlugin("Example Components")


class View(miru.View):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

        super().__init__(timeout=60)

    @miru.button("Click me!", custom_id="click_me")
    async def click_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.respond(f"{ctx.user.mention}, you clicked me!")

    # Defining select menus: https://miru.hypergonial.com/guides/selects/
    @miru.text_select(
        custom_id="select_me",
        placeholder="Choose your favourite colours...",
        min_values=1,
        max_values=3,
        options=[
            miru.SelectOption(label=colour)
            for colour in ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"]
        ],
    )
    async def colour_select(self, ctx: miru.ViewContext, select: miru.TextSelect) -> None:
        await ctx.respond(f"Your favourite colours are: {', '.join(select.values)}!")

    # Defining a custom view check: https://miru.hypergonial.com/guides/checks_timeout/#checks
    async def view_check(self, ctx: miru.ViewContext) -> bool:
        # This view will only handle interactions that belong to the
        # user who originally ran the command.
        # For every other user they will receive an error message.
        if ctx.user.id != self.user_id:
            await ctx.respond("You can't press this!", flags=hikari.MessageFlag.EPHEMERAL)
            return False

        return True

    # Handling view timeouts: https://miru.hypergonial.com/guides/checks_timeout/#timeout
    # Editing view items: https://miru.hypergonial.com/guides/editing_items/
    async def on_timeout(self) -> None:
        message = self.message
        assert message  # Since the view is bound to a message, we can assert it's not None

        for item in self.children:
            item.disabled = True

        await message.edit(components=self)
        self.stop()


@plugin.include
@arc.slash_command("components", "A command with components.")
async def components_cmd(ctx: arc.GatewayContext, miru_client: miru.Client = arc.inject()) -> None:
    view = View(ctx.user.id)
    response = await ctx.respond("Here are some components...", components=view)

    miru_client.start_view(view, bind_to=await response.retrieve_message())


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
