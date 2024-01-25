import interactions as discord
import main

class boosts(discord.Extension):
    def __init__(self, client):
        self.client: discord.Client = client

    @discord.listen()
    async def on_message(self, event: discord.events.MessageCreate):
        if event.message.type == 8:
            channel = await self.client.fetch_channel(627542044390457350)
            await channel.send(event.message.content)
