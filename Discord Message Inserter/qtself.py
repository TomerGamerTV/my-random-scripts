import asyncio
import datetime
import time
from collections import defaultdict

import discord
from discord.ext import commands
import logging
import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO)

client = discord.Client()
status_cache = {}
current_cursor = 0

# Define your desired server (guild) ID and channel IDs
GUILD_ID = 416274230133653505
# Add channel IDs if you want to restrict to specific channels
ALLOWED_CHANNEL_IDS = 1237943959142142043


def basic_permission_check(ctx):
    guild = client.get_guild(GUILD_ID)
    if guild is None:
        return False
    appropriated_user = guild.get_member(ctx.author.id)
    if appropriated_user is None:
        return False
    return appropriated_user.guild_permissions.administrator or appropriated_user.guild_permissions.manage_channels


@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    # Check if the message is from the desired server and (optionally) channel
    if message.guild.id != GUILD_ID or (ALLOWED_CHANNEL_IDS and message.channel.id not in ALLOWED_CHANNEL_IDS):
        return  # Ignore messages from other servers/channels

    # Add a log for received messages
    logging.info(f'Received message: {message.content}')
    if message.author != client.user:
        return  # Ignore messages sent by others

    if message.content.startswith('qt!transfer'):
        logging.info('Command qt!transfer received')  # Debugging print
        if not basic_permission_check(message):
            await message.channel.send(":x: Not authorized.")
            return

        args = message.content.split()[1:]  # Split message content by spaces
        if len(args) != 2:
            await message.channel.send("Usage: qt!transfer <transfer_channel_id> <to_channel_id>")
            return

        transfer_channel = args[0]
        to_channel = args[1]

        try:
            from_channel = await client.fetch_channel(int(transfer_channel))
            to_channel = await client.fetch_channel(int(to_channel))
        except discord.NotFound:
            await message.channel.send("Incorrect channel IDs.")
            return

        thread_id = 0
        if isinstance(to_channel, discord.Thread):
            thread_id = to_channel.id
            to_channel = to_channel.parent

        webhook = await to_channel.create_webhook(name="QTransfer")
        global current_cursor

        cursor = current_cursor + 1
        current_cursor += 1
        newline = '\n'
        await message.channel.send(f"Started task.\nTask ID: `{cursor}`")
        status_cache[cursor] = {"status": "Ongoing", "cursor": 0}
        async for msg in from_channel.history(limit=None, oldest_first=True):
            try:
                data = {
                    "username": msg.author.display_name,
                    "avatar_url": msg.author.avatar.url if msg.author.avatar else None,
                    "embeds": msg.embeds,
                    "content": f"<t:{int(msg.created_at.timestamp())}>\n{msg.content}\n{newline.join([att.url for att in msg.attachments])}" if msg.content else f"<t:{int(msg.created_at.timestamp())}>\n{newline.join([att.url for att in msg.attachments])}"
                }
                if thread_id != 0:
                    data["thread"] = thread_id
                status_cache[cursor]["cursor"] += 1
                await webhook.send(**data)
            except Exception as e:
                logging.error(f'Could not send message {msg.id} - {str(e)}')
        status_cache[cursor]['status'] = "Finished"

    elif message.content.startswith('qt!status'):
        logging.info('Command qt!status received')  # Debugging print
        if not basic_permission_check(message):
            await message.channel.send(":x: Not authorized.")
            return

        args = message.content.split()[1:]  # Split message content by spaces
        if len(args) != 1:
            await message.channel.send("Usage: qt!status <task_id>")
            return

        task_id = int(args[0])

        if task_id not in status_cache:
            await message.channel.send("Invalid Task ID")
            return

        await message.channel.send(f"{':white_check_mark:' if status_cache[task_id]['status'] == 'Finished' else ':x:'} Task {task_id} - {status_cache[task_id]['cursor']}")

client.run('NDE2MjczMjQxMDI4Njg5OTMx.GhA95Z.k5QGvUZ39hs4mFr4SrpV6ruSzQr-MfaWpqlovE')
