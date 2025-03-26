import arc
import hikari

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin("Example Options")


# Options Guide: https://arc.hypergonial.com/guides/options/
@plugin.include
@arc.slash_command("options", "A command with options")
async def options(
    ctx: BlockbotContext,
    str_option: arc.Option[str, arc.StrParams("A string option.", name="string")],
    int_option: arc.Option[
        int,
        arc.IntParams("An integer option.", name="integer", min=5, max=150),
    ],
    attachment_option: arc.Option[
        hikari.Attachment,
        arc.AttachmentParams("An attachment option.", name="attachment"),
    ],
    channel_option: arc.Option[
        hikari.TextableChannel | None,
        arc.ChannelParams("A textable channel option.", name="channel"),
    ] = None,
) -> None:
    """A command with lots of options."""
    embed = hikari.Embed(
        title="There are a lot of options here",
        description="Maybe too many...",
        colour=0x5865F2,
    )
    embed.set_image(attachment_option)

    embed.add_field("String option", str_option, inline=True)
    embed.add_field("Integer option", str(int_option), inline=True)
    embed.add_field(
        "Channel option",
        f"<#{channel_option.id}>" if channel_option else "Not supplied",
        inline=True,
    )

    await ctx.respond(embed=embed)


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)
