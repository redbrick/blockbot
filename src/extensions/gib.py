import interactions as discord

class Gib(discord.Extension):
    gib_choices=[ 
        discord.SlashCommandChoice(name="Webgroup", value="1166751688598761583"),
        discord.SlashCommandChoice(name="gamz", value="1089204642241581139")
    ]
    roleoption = discord.slash_option(
        name="role", required=True, opt_type=discord.OptionType.STRING,choices=gib_choices
    )
    
    @discord.slash_command("gib", "Gib user a role")
    @roleoption
    async def gib_role(self, ctx: discord.SlashContext, role):
        ctx.author.add_role(role)
        await ctx.send(f"Done! Given you {role}")
    
    @discord.slash_command("ungib", "unGib user a role")
    @roleoption
    async def ungib_role(self, ctx: discord.SlashContext, role):
        ctx.author.remove_role(role)
        await ctx.send(f"Done! Removed {role}")