import interactions as discord
import main

class boosts(discord.Extension):
    def __init__(self, client):
        self.client: discord.Client = client

    @discord.listen()
    async def on_message(self, event: discord.events.MessageCreate):
        if event.message.type in [8,9,10,11]:
            print(main.config['channel_ids']['lobby'])
            channel = await self.client.fetch_channel(main.config['channel_ids']['lobby'])
            await channel.send(event.message.system_content)
    
