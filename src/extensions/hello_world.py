"""
Example extension with simple commands
"""
from interactions import *


class HelloWorld(Extension):
    @slash_command("hello", description="Say hello!")
    async def hello(self, ctx: SlashContext):
        """A simple hello world command"""
        await ctx.send("Hello, world!")

    @slash_command(
        "base_command", description="A base command, to expand on"
    )
    async def base_command(self, ctx: SlashContext):
        ...

    @base_command.subcommand(
        "sub_command", sub_cmd_description="A sub command, to expand on"
    )
    async def sub_command(self, ctx: SlashContext):
        """A simple sub command"""
        await ctx.send("Hello, world! This is a sub command")

    @slash_command("options", description="A command with options")
    @slash_option(
        "option_str",
        "A string option",
        opt_type=OptionType.STRING,
        required=True,
    )
    @slash_option(
        "option_int",
        "An integer option",
        opt_type=OptionType.INTEGER,
        required=True,
    )
    @slash_option(
        "option_attachment",
        "An attachment option",
        opt_type=OptionType.ATTACHMENT,
        required=True,
    )
    async def options(
        self,
        ctx: SlashContext,
        option_str: str,
        option_int: int,
        option_attachment: Attachment,
    ):
        """A command with lots of options"""
        embed = Embed(
            "There are a lot of options here",
            description="Maybe too many",
            color=BrandColors.BLURPLE,
        )
        embed.set_image(url=option_attachment.url)
        embed.add_field(
            "String option",
            option_str,
            inline=False,
        )
        embed.add_field(
            "Integer option",
            str(option_int),
            inline=False,
        )
        await ctx.send(embed=embed)

    @slash_command("components", description="A command with components")
    async def components(self, ctx: SlashContext):
        """A command with components"""
        await ctx.send(
            "Here are some components",
            components=spread_to_rows(
                Button(
                    label="Click me!",
                    custom_id="click_me",
                    style=ButtonStyle.PRIMARY,
                ),
                StringSelectMenu(
                    "Select me!",
                    "No, select me!",
                    "Select me too!",
                    placeholder="I wonder what this does",
                    min_values=1,
                    max_values=2,
                    custom_id="select_me",
                ),
            ),
        )

    @component_callback("click_me")
    async def click_me(self, ctx: ComponentContext):
        """A callback for the click me button"""
        await ctx.send("You clicked me!")

    @component_callback("select_me")
    async def select_me(self, ctx: ComponentContext):
        """A callback for the select me menu"""
        await ctx.send(f"You selected {' '.join(ctx.values)}")
