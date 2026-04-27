import discord
from discord.ext import commands
import re
import asyncio
import sys
import os
from flask import Flask
from threading import Thread

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask('')

@app.route('/')
def home():
    return "Bot Bobbie's Service online", 200

def run_flask():
    app.run(host='0.0.0.0', port=8000)
def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- Bot {bot.user.name} online ---')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        content = message.content.strip()
        
       
        if "leave" in content.lower():
            if message.guild.voice_client:
                await message.guild.voice_client.disconnect()
                await message.channel.send("left vc")
            else:
                await message.channel.send("not in any vc")
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
                    await message.channel.send("this ID not vc")
                    return

                
                if message.guild.voice_client:
                    await message.guild.voice_client.disconnect(force=True)


                await channel.connect(reconnect=True, timeout=20.0, self_deaf=True, self_mute=True)
                await message.channel.send(f" Đã vào: {channel.name} (Muted & Deafened)")

            except Exception as e:
                print(f"Lỗi kết nối: {e}")
                await message.channel.send("can't connect vc")
        else:
            await message.channel.send("tag bot then paste id")
            
    await bot.process_commands(message)

async def main():
    async with bot:
        token = os.environ.get('tokens')
        if not token:
            print("Lỗi: Không tìm thấy biến môi trường 'tokens'")
            return
        await bot.start(token)

if __name__ == "__main__":
    keep_alive() 
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        pass
