import asyncio
from discord import Message

from .games.alphabet import alphabet_game
from .utils.ping import ping


async def command_router(msg: Message):
    await ping(msg)
    await alphabet_game(msg)

    
