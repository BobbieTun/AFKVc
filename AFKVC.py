import discord
from discord.ext import commands
import re
import asyncio
import sys

# 1. FIX QUAN TRỌNG CHO PYTHON 3.13 TRÊN WINDOWS
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} online')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Logic: Tag bot + ID để vào
    if bot.user.mentioned_in(message):
        content = message.content.strip()
        
        if "leave" in content.lower():
            if message.guild.voice_client:
                await message.guild.voice_client.disconnect()
                await message.channel.send("left")
            else:
                await message.channel.send("not in vc")
            return

        all_ids = re.findall(r'\d{17,20}', content)
        target_id = None
        for cid in all_ids:
            if int(cid) != bot.user.id:
                target_id = int(cid)
                break
        
        if target_id:
            try:
                channel = bot.get_channel(target_id)
                if not channel:
                    channel = await bot.fetch_channel(target_id)
                if not isinstance(channel, discord.VoiceChannel):
                    await message.channel.send("not vc")
                    return
                if message.guild.voice_client:
                    try:
                        await message.guild.voice_client.disconnect(force=True)
                    except:
                        pass
                await channel.connect(reconnect=True, timeout=20.0)
                await message.channel.send(f"joined: {channel.name}")
            except discord.NotFound:
                await message.channel.send("not found")
            except Exception as e:
                print(f"Loi: {e}")
                await message.channel.send("cant connect")
        else:
            await message.channel.send("use id after tag")
    await bot.process_commands(message)

async def main():
    async with bot:
        await bot.start('MTM1MDE4NDg0NzU1MjkzODEwNw.G3BZO7.CGoGSYiHG-kqg119rRmeiyBTZmVAZYvXLyOrAg')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except RuntimeError: 

        pass

