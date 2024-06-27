import discord
from discord.ext import commands
import logging
import aiohttp


bot = commands.Bot(command_prefix="qt!", help_command=None, intents=discord.Intents.all())
status_cache = {}
current_cursor = 0


def basic_permission_check():
    async def predicate(ctx):
        guild = await bot.fetch_guild(1194043323216834740)
        if guild is None:
            return False
        try:
            appropriated_user = await guild.fetch_member(ctx.author.id)
        except discord.HTTPException:
            return False
        
        if appropriated_user.guild_permissions.administrator or appropriated_user.guild_permissions.manage_channels:
            return True
    return commands.check(predicate)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return await ctx.send(":x: Not authorized.")
    raise error

@bot.event
async def on_ready():
    if 'jishaku' not in bot.cogs.keys():
        await bot.load_extension('jishaku')
    else:
        logging.info('Already loaded Jishaku - not reloading.')
    await bot.tree.sync()

@bot.hybrid_command(
    name="transfer",
    aliases=["tf"],
    description="Cross-server transfer method."
)
@basic_permission_check()
async def transfer_content(ctx: commands.Context, transfer_channel: str, to_channel: str):
    try:
        from_channel: discord.TextChannel = await bot.fetch_channel(int(transfer_channel))
        to_channel: discord.TextChannel = await bot.fetch_channel(int(to_channel))
    except discord.NotFound:
        return await ctx.send("Incorrect channel IDs.")
    # if to_channel.guild.id != 1194043323216834740:
    #     return await ctx.send("Messages can only be transferred into the staff server.")
    
    thread_id = 0
    if isinstance(to_channel, discord.Thread):
        thread_id = to_channel.id
        to_channel = to_channel.parent
        

    webhook: discord.Webhook = await to_channel.create_webhook(name="QTransfer")
    global current_cursor

    cursor = current_cursor + 1
    current_cursor += 1
    newline = '\n'
    await ctx.send(f"Started task.\nTask ID: `{cursor}`")
    status_cache[cursor] = {"status": "Ongoing", "cursor": 0}
    async for message in from_channel.history(limit=None, oldest_first=True):
        try:
            data = {
                "username": message.author.global_name,
                "avatar_url": message.author.display_avatar.url,
                "embeds": message.embeds,
                "content": f"<t:{int(message.created_at.timestamp())}>\n{('{}'.format(newline)).join([i.proxy_url for i in message.attachments])}" if not message.content else f"<t:{int(message.created_at.timestamp())}>\n{message.content}\n{('{}'.format(newline)).join([i.proxy_url for i in message.attachments])}"
            }
            if thread_id != 0:
                data["thread"] = thread_id
            status_cache[cursor]["cursor"] += 1
            await webhook.send(**data)
        except Exception as e:
            print(f'Could not send message {message.id} - {str(e)}')
    status_cache[cursor]['status'] = "Finished"
            

@bot.hybrid_command(
    name="status"
)
@basic_permission_check()
async def status(ctx: commands.Context, id: int):
    if id not in status_cache.keys():
        return await ctx.send("Invalid Task ID")
    await ctx.send(f"{':white_check_mark:' if status_cache[id]['status'] == 'Finished' else ':x:'} Task {id} - {status_cache[id]['cursor']}")

bot.run('NDE2MjczMjQxMDI4Njg5OTMx.GhA95Z.k5QGvUZ39hs4mFr4SrpV6ruSzQr-MfaWpqlovE')
