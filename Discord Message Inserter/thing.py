from copy import copy
import asyncio
for _ in _guild.channels:
    try:
        await _.delete()
    except:
        pass

categories = [1254459646312190024, 1250488968437436516, 1237936809581740063, 1237937122330153020,
              1237937155376943154, 1237937193725591627, 1237937317457563698, 1237937678125764719]

category_channels = [await _bot.fetch_channel(cat) for cat in categories]
transfer_server = await _bot.fetch_guild(416274230133653505)

mapping = {}
submapping = {}
coroutines = []
initial_starting_point = 0
for item in category_channels:
    mapped_channel = await transfer_server.create_category(item.name)
    mapping[item.id] = mapped_channel.id
    if initial_starting_point == 0:
        initial_starting_point = item.position
    for channel in item.text_channels:
        submapped_channel = await mapped_channel.create_text_channel(channel.name)
        submapping[channel.id] = submapped_channel.id
        coroutines.append(_ctx.invoke(_bot.get_command(
            'transfer'), channel.id, submapped_channel.id))
    for channel in item.channels:
        if not isinstance(channel, discord.ForumChannel):
            continue
        forum_channel = await mapped_channel.create_forum(channel.name)
        await forum_channel.edit(position=channel.position - initial_starting_point)
        for thread in channel.threads:
            if isinstance(thread, discord.channel.ThreadWithMessage):
                thread = thread.thread
            submapped_thread, _ = await forum_channel.create_thread(name=thread.name, content=f"<t:{int(thread.created_at.timestamp())}>")
            coroutines.append(_ctx.invoke(_bot.get_command(
                'transfer'), thread.id, submapped_thread.id))

await asyncio.gather(*coroutines)
