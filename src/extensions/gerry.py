import arc
import hikari

gerry = arc.GatewayPlugin(name="gerry")

image = "https://cdn.redbrick.dcu.ie/blockbot/gerry.jpg"


@gerry.include
@arc.slash_command("gerry", "So tell me Frank!")
async def gerry_command(
    ctx: arc.GatewayContext,
    user: arc.Option[
        hikari.User | None,
        arc.UserParams("The user to send a gerry to."),
    ] = None,
) -> None:
    """Send a gerry!"""
    if user is not None:
        description = f"So tell me {user.mention}!"
    else:
        description = "So tell me Frank!"

    embed = hikari.Embed(
        title="Gerry",
        description=description,
        colour=0xffc753,  # the yellow of gerry's jacket
    )
    embed = embed.set_image(image)

    await ctx.respond(embed)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(gerry)
