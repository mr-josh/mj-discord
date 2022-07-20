from discord import Message


async def ping(msg: Message):
    if msg.content != "ping":
        return
    await msg.channel.send("pong")
