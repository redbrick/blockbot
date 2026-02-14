import io

import aiohttp
import arc
import hikari
from arc.internal.types import ChoiceT, ClientT
from minio import Minio
from minio.error import S3Error

from src.config import (
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_REGION,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    ROLE_IDS,
    Feature,
)
from src.hooks import restrict_to_roles
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

minio = BlockbotPlugin(name="minio", required_features=[Feature.MINIO])

minio_client = Minio(
    MINIO_ENDPOINT,
    region=MINIO_REGION,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)


async def get_bucket_choices(ctx: arc.AutocompleteData[ClientT, ChoiceT]) -> list[str]:
    """Fetch available buckets from MinIO for autocomplete."""

    # Check if the user has the required role to access MinIO commands
    if not ctx.interaction.member:
        return []

    if ROLE_IDS["committee"] not in ctx.interaction.member.role_ids:
        return []

    response = minio_client.list_buckets()
    buckets = [bucket.name for bucket in response]
    if ctx.focused_value:
        buckets = [b for b in buckets if str(ctx.focused_value).lower() in b.lower()]
    return buckets[:25]


def minio_prefix_exists(bucket_name: str, prefix: str) -> bool:
    """Check if a prefix (folder) exists in a MinIO bucket."""

    objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
    try:
        next(objects)  # Will raise StopIteration if no object exists
        return True
    except StopIteration:
        return False


@minio.include
@arc.with_hook(restrict_to_roles(role_ids=[ROLE_IDS["committee"]]))
@arc.slash_command("upload", "Upload a file to the storage server.")
async def upload_command(
    ctx: BlockbotContext,
    bucket_name: arc.Option[
        str,
        arc.StrParams(
            "The bucket to add the files to.", autocomplete_with=get_bucket_choices
        ),
    ],
    path: arc.Option[
        str, arc.StrParams("The path to the folder to save the file. (e.g. `folder/`)")
    ],
    file: arc.Option[hikari.Attachment, arc.AttachmentParams("The file to upload.")],
    aiohttp_client: aiohttp.ClientSession = arc.inject(),
) -> None:
    if not file:
        await ctx.respond(
            "❌ Please attach a file to upload.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # Normalize path
    path = path.rstrip("/") if path else ""

    if path and not path.endswith("/"):
        path += "/"

    # The file to upload. In Discord URL format.
    source_file = file.url

    # Check if bucket exists in MinIO
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        await ctx.respond(
            f"❌ Bucket `{bucket_name}` does not exist on the storage server.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # Check if path to the folder is valid and exists in the bucket
    if path and not minio_prefix_exists(bucket_name, path):
        await ctx.respond(
            f"❌ The specified path `{path}` does not exist in bucket `{bucket_name}`.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    # Temporarily download the file to a local path before uploading to MinIO
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
            f"{path}{file.filename}",
            io.BytesIO(data),
            len(data),
            content_type=response.content_type,
        )
    await ctx.respond(
        f"✅ File `{file.filename}` uploaded successfully at `{bucket_name}/{path}{file.filename}`.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@minio.set_error_handler
async def minio_error_handler(ctx: BlockbotContext, error: Exception) -> None:
    if isinstance(error, S3Error):
        if error.code == "XMinioInvalidObjectName":
            await ctx.respond(
                "❌ Invalid path/file name. Please ensure the path/file name does not contain invalid characters and is not too long.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await ctx.respond(
                f"❌ MinIO error: `{error.code} {error.message}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        return
    if isinstance(error, aiohttp.ClientResponseError):
        await ctx.respond(
            f"❌ Failed to download the file. Status code: `{error.status} {error.message}`",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(minio)
