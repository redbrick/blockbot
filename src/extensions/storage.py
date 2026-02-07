import arc
import hikari
from minio import Minio
from minio.error import S3Error

from src.models import Blockbot, BlockbotContext, BlockbotPlugin

minio = BlockbotPlugin(name="minio")

@minio.include
@arc.slash_command("upload", "Upload a file to the storage server.")
async def upload_command(
        ctx: BlockbotContext,
        # file: arc.Option[hikari.Attachment, arc.AttachmentParams("The file to upload.")],
) -> None:
    minio_client = Minio(
        "host.docker.internal:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )

    # if not file:
    #     await ctx.respond(
    #         "❌ Please attach a file to upload.",
    #         flags=hikari.MessageFlag.EPHEMERAL,
    #     )
    #     return
    #
    # # The file to upload, change this path if needed
    # source_file = file.url

    await ctx.respond(minio_client.list_buckets() or "Nope")
    #
    # # The destination bucket and filename on the MinIO server
    # bucket_name = "python-test-bucket"
    # destination_file = "my-test-file.webp"
    #
    # # Make the bucket if it doesn't exist.
    # found = minio_client.bucket_exists(bucket_name)
    # if not found:
    #     minio_client.make_bucket(bucket_name)
    #     await ctx.respond(
    #         f"✅ Created bucket `{bucket_name}` on the storage server.",
    #         flags=hikari.MessageFlag.EPHEMERAL,
    #     )
    # else:
    #     await ctx.respond(
    #         f"✅ Bucket `{bucket_name}` Exists on the storage server.",
    #         flags=hikari.MessageFlag.EPHEMERAL,
    #     )

    # # Upload the file, renaming it in the process
    # minio_client.fput_object(
    #     bucket_name, destination_file, source_file,
    # )
    # await ctx.respond(
    #     f"✅ File `{file.filename}` uploaded successfully as `{destination_file}`.",
    #     flags=hikari.MessageFlag.EPHEMERAL,
    # )




@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(minio)
