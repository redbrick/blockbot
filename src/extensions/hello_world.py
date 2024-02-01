"""
Example extension with simple commands
"""
import arc
import hikari

plugin = arc.GatewayPlugin(name='Hello World')

@plugin.include
@arc.slash_command('hello', 'Say hello!')
async def hello(ctx: arc.GatewayContext) -> None:
    """A simple hello world command"""
    await ctx.respond('Hello from hikari!')

group = plugin.include_slash_group('base_command', 'A base command, to expand on')

@group.include
@arc.slash_subcommand('sub_command', 'A sub command, to expand on')
async def sub_command(ctx: arc.GatewayContext) -> None:
    """A simple sub command"""
    await ctx.respond('Hello, world! This is a sub command')

@plugin.include
@arc.slash_command('options', 'A command with options')
async def options(
    ctx: arc.GatewayContext,
    option_str: arc.Option[str, arc.StrParams('A string option')],
    option_int: arc.Option[int, arc.IntParams('An integer option')],
    option_attachment: arc.Option[hikari.Attachment, arc.AttachmentParams('An attachment option')],
) -> None:
    """A command with lots of options"""
    embed = hikari.Embed(
      title='There are a lot of options here',
      description='Maybe too many',
      colour=0x5865F2
    )
    embed.set_image(option_attachment)
    embed.add_field('String option', option_str, inline=False)
    embed.add_field('Integer option', str(option_int), inline=False)
    await ctx.respond(embed=embed)

@plugin.include
@arc.slash_command('components', 'A command with components')
async def components(ctx: arc.GatewayContext) -> None:
    """A command with components"""
    builder = ctx.client.rest.build_message_action_row()
    select_menu = builder.add_text_menu(
      'select_me',
      placeholder='I wonder what this does',
      min_values=1,
      max_values=2
    )
    for opt in ('Select me!', 'No, select me!', 'Select me too!'):
        select_menu.add_option(opt, opt)

    button = ctx.client.rest.build_message_action_row().add_interactive_button(
        hikari.ButtonStyle.PRIMARY, 'click_me', label='Click me!'
    )

    await ctx.respond('Here are some components', components=[builder, button])

@plugin.listen()
async def on_interaction(event: hikari.InteractionCreateEvent) -> None:
    interaction = event.interaction

    # Discussions are underway for allowing to listen for a "ComponentInteractionEvent" directly
    # instead of doing this manual filtering: https://github.com/hikari-py/hikari/issues/1777
    if not isinstance(interaction, hikari.ComponentInteraction):
        return

    if interaction.custom_id == 'click_me':
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f'{interaction.user.mention}, you clicked me!'
        )
    elif interaction.custom_id == 'select_me':
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            f"{interaction.user.mention}, you selected {' '.join(interaction.values)}",
        )

@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
