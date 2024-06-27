import discord
import aiohttp
import asyncio

# Replace these with your values
TOKEN = 'NDE2MjczMjQxMDI4Njg5OTMx.GhA95Z.k5QGvUZ39hs4mFr4SrpV6ruSzQr-MfaWpqlovE'
MESSAGE_LIMIT = 50  # Number of past messages to clone
COOLDOWN_SECONDS = 5  # Cooldown to avoid rate limits

# Channel IDs and their corresponding webhook URLs
CHANNELS_AND_WEBHOOKS = {
    # Replace with your source channel ID and webhook URL
    "1237946650346131537": "https://discord.com/api/webhooks/1255225145296158720/-FtK5MxpYbQ-7XwK0qd4OOZSucdWH2c4J02HASI-IUuqaE6uTmYCALdFFfl0eDaZ9t0e",
}

intents = discord.Intents.default()
intents.messages = True


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await self.clone_past_messages()

    async def on_message(self, message):
        if str(message.channel.id) in CHANNELS_AND_WEBHOOKS and CHANNELS_AND_WEBHOOKS[str(message.channel.id)] != "YOUR_WEBHOOK_URL_":
            await self.send_to_webhook(message)

    async def clone_past_messages(self):
        for channel_id, webhook_url in CHANNELS_AND_WEBHOOKS.items():
            if channel_id.startswith("YOUR_CHANNEL_ID_") or webhook_url.startswith("YOUR_WEBHOOK_URL_"):
                continue

            channel = self.get_channel(int(channel_id))
            if channel is None:
                print(f"Channel with ID {channel_id} not found.")
                continue

            messages = await channel.history(limit=MESSAGE_LIMIT).flatten()
            for message in reversed(messages):
                await self.send_to_webhook(message)

    async def send_to_webhook(self, message):
        webhook_url = CHANNELS_AND_WEBHOOKS[str(message.channel.id)]
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                webhook_url, adapter=discord.AsyncWebhookAdapter(session))
            await webhook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar.url)
            await asyncio.sleep(COOLDOWN_SECONDS)


client = MyClient(intents=intents)
client.run(TOKEN, bot=False)
