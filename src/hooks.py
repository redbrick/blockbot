import typing

import arc
import hikari


async def _restrict_to_roles(
    ctx: arc.GatewayContext,
    role_ids: typing.Sequence[int],
) -> arc.HookResult:
    assert ctx.member

    if not any(role_id in ctx.member.role_ids for role_id in role_ids):
        await ctx.respond(
            "❌ This command is restricted. Only allowed roles are permitted to use this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return arc.HookResult(abort=True)

    return arc.HookResult()  # by default, abort is set to False


# TODO: make response type a TypeVar for reuse (WrappedHookResult)
def restrict_to_roles(
    role_ids: typing.Sequence[int],
) -> typing.Callable[[arc.GatewayContext], typing.Awaitable[arc.HookResult]]:
    """Any command which uses this hook requires that the command be disabled in DMs as a guild role is required for this hook to function."""

    async def func(ctx: arc.GatewayContext) -> arc.HookResult:
        return await _restrict_to_roles(ctx, role_ids)

    return func


async def _restrict_to_channels(
    ctx: arc.GatewayContext,
    channel_ids: typing.Sequence[int],
) -> arc.HookResult:
    if ctx.channel_id not in channel_ids:
        await ctx.respond(
            "❌ This command cannot be used in this channel.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return arc.HookResult(abort=True)

    return arc.HookResult()


def restrict_to_channels(
    channel_ids: typing.Sequence[int],
) -> typing.Callable[[arc.GatewayContext], typing.Awaitable[arc.HookResult]]:
    async def func(ctx: arc.GatewayContext) -> arc.HookResult:
        return await _restrict_to_channels(ctx, channel_ids)

    return func
