import os

from discord import Client, Intents, Message
from dotenv import load_dotenv

from .commands.router import command_router

load_dotenv()
TOKEN = os.getenv("TOKEN")

class MJClient(Client):
    """
    Join URL: https://discord.com/api/oauth2/authorize?client_id=999238922817245266&permissions=8&scope=bot%20applications.commands
    """

    async def on_ready(self):
        print("Logged on as", self.user)

    async def on_message(self, message: Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        await command_router(message)

# Start the bot
intents = Intents.default()
client = MJClient(intents=intents)
client.run(TOKEN)
