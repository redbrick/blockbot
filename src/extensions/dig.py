import arc
import hikari
from dns import resolver

dig = arc.GatewayPlugin(name="dig")


@dig.include
@arc.slash_command("dig", "Query DNS records for a domain")
async def dig_command(
    ctx: arc.GatewayContext,
    domain: arc.Option[str, arc.StrParams("The domain to query")],
    record_type: arc.Option[
        str,
        arc.StrParams(
            "Type of record to query",
            choices=["A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "SRV", "TXT"],
        ),
    ] = "A",
) -> None:
    """Query DNS records for a domain"""
    record_type = record_type.upper()

    try:
        response = resolver.resolve(domain, record_type)
    except resolver.NoAnswer as e:
        await ctx.respond(f"❌ {e}", flags=hikari.MessageFlag.EPHEMERAL)
        return

    result = "\n".join(str(rdata) for rdata in response)
    embed = hikari.Embed(
        title=f"{record_type} records for `{domain}`:",
        description=f"""```{result}```""",
    )
    await ctx.respond(embed=embed)


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(dig)
