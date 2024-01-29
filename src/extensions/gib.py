import interactions as discord

class Gib(discord.Extension):
    gib_choices=[ 
        discord.SlashCommandChoice(name="Webgroup", value="1166751688598761583"),
        discord.SlashCommandChoice(name="gamz", value="1089204642241581139"),
        discord.SlashCommandChoice(name="Croomer", value="1172696659097047050"),
    ]
    roleoption = discord.slash_option(
        name="role", description='', required=True, opt_type=discord.OptionType.STRING,choices=gib_choices
    )
    
    @discord.slash_command("gib", description="Gib user a role")
    @roleoption
    async def gib_role(self, ctx: discord.SlashContext, role):
        ctx.author.add_role(role)
        await ctx.send(f"Done! Gabe u {ctx.guild.get_role(role).name}")
    
    @discord.slash_command("ungib", description="unGib user a role")
    @roleoption
    async def ungib_role(self, ctx: discord.SlashContext, role):
        ctx.author.remove_role(role)
        await ctx.send(f"Done! UNGabe {ctx.guild.get_role(role).name}")
