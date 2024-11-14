import arc
import hikari
import typing


def restrict_to_roles(
    ctx: arc.GatewayContext, role_ids: typing.Sequence[hikari.Snowflake]
) -> arc.HookResult:
    if not any(role_id in ctx.author.role_ids for role_id in role_ids):
        ctx.respond(
            "❌ This command is restricted. Only allowed roles are permitted to use this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return arc.HookResult(abort=True)
    return arc.HookResult()


def restrict_to_channels(
    ctx: arc.GatewayContext, channel_ids: typing.Sequence[hikari.Snowflake]
) -> arc.HookResult:
    if ctx.channel_id not in channel_ids:
        ctx.respond(
            "❌ This command cannot be used in this channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return arc.HookResult(abort=True)
    return arc.HookResult()
