import arc
import hikari

from src.utils import role_mention

plugin = arc.GatewayPlugin(name="User Roles")

role = plugin.include_slash_group("role", "Get/remove assignable roles.")

role_choices = [
    hikari.CommandChoice(name="Webgroup", value="1166751688598761583"),
    hikari.CommandChoice(name="Gamez", value="1089204642241581139"),
    hikari.CommandChoice(name="Croomer", value="1172696659097047050"),
]

@role.include
@arc.slash_subcommand("add", "Add an assignable role.")
async def add_role(
    ctx: arc.GatewayContext,
    role: arc.Option[str, arc.StrParams("The role to add.", choices=role_choices)]
) -> None:
    assert ctx.guild_id
    assert ctx.member

    if int(role) in ctx.member.role_ids:
        return await ctx.respond(
          f"You already have the {role_mention(role)} role.",
          flags=hikari.MessageFlag.EPHEMERAL
        )

    await ctx.client.rest.add_role_to_member(
        ctx.guild_id, ctx.author, int(role), reason="Self-service role."
    )
    await ctx.respond(
      f"Done! Added {role_mention(role)} to your roles.",
      flags=hikari.MessageFlag.EPHEMERAL
    )

@role.include
@arc.slash_subcommand("remove", "Remove an assignable role.")
async def remove_role(
    ctx: arc.GatewayContext,
    role: arc.Option[str, arc.StrParams("The role to remove.", choices=role_choices)]
) -> None:
    assert ctx.guild_id
    assert ctx.member

    if int(role) not in ctx.member.role_ids:
        return await ctx.respond(
          f"You don't have the {role_mention(role)} role.",
          flags=hikari.MessageFlag.EPHEMERAL
        )

    await ctx.client.rest.remove_role_from_member(
        ctx.guild_id, ctx.author, int(role), reason=f"{ctx.author} removed role."
    )
    await ctx.respond(
      f"Done! Removed {role_mention(role)} from your roles.",
      flags=hikari.MessageFlag.EPHEMERAL
    )

@role.set_error_handler
async def role_error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    role = ctx.get_option("role", arc.OptionType.STRING)
    assert role is not None

    if isinstance(exc, hikari.ForbiddenError):
        return await ctx.respond(
          f"❌ Blockbot is not permitted to self-service the {role_mention(role)} role.",
          flags=hikari.MessageFlag.EPHEMERAL
        )
    
    if isinstance(exc, hikari.NotFoundError):
        return await ctx.respond(
          f"❌ Blockbot can't find that role.",
          flags=hikari.MessageFlag.EPHEMERAL
        )

    raise exc

@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
