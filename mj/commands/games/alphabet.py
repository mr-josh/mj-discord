from pytz import timezone
from discord import Message

from mj.db.client import dbc
from mj.utils.date import date_int

TIMEZONE = timezone("Australia/Sydney")

async def fail(msg: Message):
    await dbc["Game"].update_one(
        {
            "type": "alphabet",
            "status": "active",
            "channel_id": msg.channel.id,
            "guild_id": msg.guild.id,
        },
        {
            "$set": {
                "status": "failed",
                "last_sent": date_int(msg.created_at.astimezone(TIMEZONE)),
                "progress.failed": msg.author.id,
            }
        },
    )

async def alphabet_game(msg: Message):
    # Entry checks
    if not isinstance(msg.content, str):
        return

    # Game checks
    game = await dbc["Game"].find_one(
        {
            "type": "alphabet",
            "status": "active",
            "channel_id": msg.channel.id,
            "guild_id": msg.guild.id,
        }
    )

    # If we're starting a game
    if game is None and msg.content == "A":
        # Start a new game
        game = await dbc["Game"].insert_one(
            {
                "type": "alphabet",
                "status": "active",
                "channel_id": msg.channel.id,
                "guild_id": msg.guild.id,
                "last_sent": date_int(msg.created_at.astimezone(TIMEZONE)),
                "progress": {
                    "A": msg.author.id
                },
            }
        )

        await msg.add_reaction("✅")

        return

    # If no game exists and we're not starting a game, then just bail
    if game is None:
        return

    # Progress checks
    progress_keys = list(game["progress"].keys())
    # If message is next letter in the alphabet
    if msg.content == chr(ord(progress_keys[-1]) + 1):
        # If we sent the next letter on the same day, then fail
        if game["last_sent"] == date_int(msg.created_at.astimezone(TIMEZONE)):
            await fail(msg)
            await msg.add_reaction("❌")
            await msg.channel.send("Too early! You should've sent it tomorrow!")
            return

        # If we sent the next letter on a day after the next, then fail
        if date_int(msg.created_at.astimezone(TIMEZONE)) - game["last_sent"] > 1:
            await fail(msg)
            await msg.add_reaction("❌")
            await msg.channel.send("Too late! You should've sent it earlier!")
            return

        # Update the progress since move was made successfully
        await dbc["Game"].update_one(
            {
                "type": "alphabet",
                "status": "active",
                "channel_id": msg.channel.id,
                "guild_id": msg.guild.id,
            },
            {
                "$set": {
                    "last_sent": date_int(msg.created_at.astimezone(TIMEZONE)),
                    "progress."
                    + msg.content: msg.author.id
                }
            },
        )

        await msg.add_reaction("✅")

        # If we're on the last letter, then end the game
        if msg.content == "Z":
            await dbc["Game"].update_one(
                {
                    "type": "alphabet",
                    "status": "active",
                    "channel_id": msg.channel.id,
                    "guild_id": msg.guild.id,
                },
                {
                    "$set": {
                        "status": "complete",
                    }
                },
            )

            # TODO: Calculate score
            await msg.channel.send("🎉 Chain complete! 🎉\nAwarding points...")

        return

    # Anything else means the game is over
    await fail(msg)

    await msg.add_reaction("❌")
    await msg.channel.send("You broke the chain :c")
