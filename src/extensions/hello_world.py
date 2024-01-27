"""
Example extension with simple commands
"""
import interactions as discord


class HelloWorld(discord.Extension):
    @discord.slash_command("hello", description="Say hello!")
    async def hello(self, ctx: discord.SlashContext):
        """A simple hello world command"""
        await ctx.send("Hello, world!")

    @discord.slash_command(
        "base_command", description="A base command, to expand on"
    )
    async def base_command(self, ctx: discord.SlashContext):
        ...

    @base_command.subcommand(
        "sub_command", sub_cmd_description="A sub command, to expand on"
    )
    async def sub_command(self, ctx: discord.SlashContext):
        """A simple sub command"""
        await ctx.send("Hello, world! This is a sub command")

    @discord.slash_command("options", description="A command with options")
    @discord.slash_option(
        "option_str",
        "A string option",
        opt_type=discord.OptionType.STRING,
        required=True,
    )
    @discord.slash_option(
        "option_int",
        "An integer option",
        opt_type=discord.OptionType.INTEGER,
        required=True,
    )
    @discord.slash_option(
        "option_attachment",
        "An attachment option",
        opt_type=discord.OptionType.ATTACHMENT,
        required=True,
    )
    async def options(
        self,
        ctx: discord.SlashContext,
        option_str: str,
        option_int: int,
        option_attachment: discord.Attachment,
    ):
        """A command with lots of options"""
        embed = discord.Embed(
            "There are a lot of options here",
            description="Maybe too many",
            color=discord.BrandColors.BLURPLE,
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

    @discord.slash_command("components", description="A command with components")
    async def components(self, ctx: discord.SlashContext):
        """A command with components"""
        await ctx.send(
            "Here are some components",
            components=discord.spread_to_rows(
                discord.Button(
                    label="Click me!",
                    custom_id="click_me",
                    style=discord.ButtonStyle.PRIMARY,
                ),
                discord.StringSelectMenu(
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

    @discord.component_callback("click_me")
    async def click_me(self, ctx: discord.ComponentContext):
        """A callback for the click me button"""
        user = ctx.author
        await ctx.send(f"{user.mention}, you clicked me!")

    @discord.component_callback("select_me")
    async def select_me(self, ctx: discord.ComponentContext):
        """A callback for the select me menu"""
        user = ctx.author
        await ctx.send(f"{user.mention}, you selected {' '.join(ctx.values)}")
