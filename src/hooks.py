import logging
import typing
from typing import Awaitable, Callable

import arc
import hikari

from src.config import Feature
from src.models import BlockbotContext

type WrappedHookResult = typing.Callable[
    [BlockbotContext], typing.Awaitable[arc.HookResult]
]

logger = logging.getLogger(__name__)


def can_be_disabled(func: WrappedHookResult) -> WrappedHookResult:
    async def wrapper(ctx: BlockbotContext) -> arc.HookResult:
        if not Feature.PERMISSION_HOOKS.enabled:
            logger.warning(
                f"permission hook disabled; bypassing restrictions for '{ctx.command.name}' command"
            )
            return arc.HookResult(abort=False)

        return await func(ctx)

    return wrapper


async def _restrict_to_roles(
    ctx: BlockbotContext,
    role_ids: typing.Sequence[int],
) -> arc.HookResult:
    assert ctx.member

    if not all(role_id in ctx.member.role_ids for role_id in role_ids):
        await ctx.respond(
            "❌ This command is restricted. Only allowed roles are permitted to use this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return arc.HookResult(abort=True)

    return arc.HookResult()  # by default, abort is set to False


class RoleRestrictedHook:
    def __init__(
        self,
        role_ids: typing.Sequence[int],
        func: Callable[[BlockbotContext], Awaitable[arc.HookResult]],
    ) -> None:
        self.role_ids = role_ids
        self.func = func

    async def __call__(self, ctx: BlockbotContext) -> arc.HookResult:
        return await self.func(ctx)


def restrict_to_roles(
    role_ids: typing.Sequence[int],
) -> RoleRestrictedHook:
    """Any command which uses this hook requires that the command be disabled in DMs as a guild role is required for this hook to function."""

    @can_be_disabled
    async def func(ctx: BlockbotContext) -> arc.HookResult:
        return await _restrict_to_roles(ctx, role_ids)

    # Return the custom wrapper with role_ids
    return RoleRestrictedHook(role_ids, func)


async def _restrict_to_channels(
    ctx: BlockbotContext,
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
) -> WrappedHookResult:
    @can_be_disabled
    async def func(ctx: BlockbotContext) -> arc.HookResult:
        return await _restrict_to_channels(ctx, channel_ids)

    return func
