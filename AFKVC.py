import discord
from discord.ext import commands, tasks
import re
import asyncio
import os
from flask import Flask
from threading import Thread

# --- CẤU HÌNH HOST ---
app = Flask('')
@app.route('/')
def home(): return "bot onl", 200
def run_flask(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run_flask, daemon=True).start()

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.target_room = None

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'bot {bot.user.name} da len')
    if not auto_reconnect.is_running():
        auto_reconnect.start()
@tasks.loop(seconds=20)
async def auto_reconnect():
    if not bot.target_room: return
    channel = bot.get_channel(bot.target_room)
    if not channel: return
    vc = channel.guild.voice_client
    if not vc or not vc.is_connected():
        try:
            await channel.connect(self_deaf=True, self_mute=True)
            print("da tu vao lai room")
        except: pass


@bot.tree.command(name="join", description="cho bot join room")
async def join(interaction: discord.Interaction, room_id: str):
    try:
        rid = int(room_id)
        channel = bot.get_channel(rid) or await bot.fetch_channel(rid)
        if not isinstance(channel, discord.VoiceChannel):
            return await interaction.response.send_message("id k phai vc", ephemeral=True)
        
        bot.target_room = rid
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)
        await interaction.guild.me.edit(mute=True, deafen=True)
        await interaction.response.send_message(f"da treo tai {channel.name}")
    except:
        await interaction.response.send_message("id loi r", ephemeral=True)

@bot.tree.command(name="limit", description="set gioi han nguoi vao vc")
async def set_limit(interaction: discord.Interaction, limit: int):
    if not interaction.user.voice:
        return await interaction.response.send_message("vô room đi r mới chỉnh dc", ephemeral=True)
    
    channel = interaction.user.voice.channel
    await channel.edit(user_limit=limit)
    await interaction.response.send_message(f"da set limit room {channel.name} la {limit}")
@bot.tree.command(name="lock", description="khoa vc rieng tu")
async def lock_vc(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("vô room đi đã", ephemeral=True)
    
    channel = interaction.user.voice.channel
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    overwrite.view_channel = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"da khoa room {channel.name}")
@bot.tree.command(name="allow", description="cho phep user vao va chat")
async def allow(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.voice:
        return await interaction.response.send_message("vô room đi cha", ephemeral=True)
    
    channel = interaction.user.voice.channel
    await channel.set_permissions(member, view_channel=True, connect=True, send_messages=True)
    await interaction.response.send_message(f"da mo quyen cho {member.display_name}")

@bot.tree.command(name="remove_allow", description="go quyen cua user")
async def remove_allow(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.voice:
        return await interaction.response.send_message("vô room đi đã", ephemeral=True)
    
    channel = interaction.user.voice.channel
    await channel.set_permissions(member, overwrite=None)
    await interaction.response.send_message(f"da xoa quyen cua {member.display_name}")
token = os.environ.get('tokens')
if __name__ == "__main__":
    keep_alive()
    bot.run(token)
