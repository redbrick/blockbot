import io

import arc
import hikari
import aiohttp
from minio import Minio
from minio.error import S3Error

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

minio = BlockbotPlugin(name="minio")

minio_client = Minio(
    "host.docker.internal:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

async def get_bucket_choices(ctx: arc.AutocompleteData) -> list[str]:
    """Fetch available buckets from MinIO for autocomplete."""
    try:
        response = minio_client.list_buckets()
        return [bucket.name for bucket in response]
    except S3Error:
        return []

@minio.include
@arc.slash_command("upload", "Upload a file to the storage server.")
async def upload_command(
        ctx: BlockbotContext,
        bucket_name: arc.Option[str, arc.StrParams("The bucket to add the files to.", autocomplete_with=get_bucket_choices)],
        file: arc.Option[hikari.Attachment, arc.AttachmentParams("The file to upload.")],
        aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:

    if not file:
        await ctx.respond(
            "❌ Please attach a file to upload.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # The file to upload, change this path if needed
    source_file = file.url

    # Make the bucket if it doesn't exist.
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
        await ctx.respond(
            f"✅ Created bucket `{bucket_name}` on the storage server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        await ctx.respond(
            f"✅ Bucket `{bucket_name}` Exists on the storage server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


    # Temporarily download the file to a local path before uploading to MinIO
    local_path = f"/tmp/{file.filename}"
    async with aiohttp_client.get(source_file) as response:
        if response.status != 200:
            await ctx.respond(
                f"❌ Failed to download the file. Status code: `{response.status}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        data = await response.read()
        minio_client.put_object(
            bucket_name,
            file.filename,
            io.BytesIO(data),
            len(data)
        )
    await ctx.respond(
        f"✅ File `{file.filename}` uploaded successfully as `{file.filename}`.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )




@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(minio)
