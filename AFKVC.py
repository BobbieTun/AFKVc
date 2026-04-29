import discord
from discord.ext import commands, tasks
import re
import asyncio
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "bot onl", 200
def run_flask(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run_flask, daemon=True).start()


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
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        content = message.content.strip().lower()
        
       
        if "leave" in content:
            if message.guild.voice_client:
                bot.target_room = None 
                await message.guild.voice_client.disconnect()
                await message.channel.send("da out")
            else:
                await message.channel.send("dang o dau ma out")
            return
        all_ids = re.findall(r'\d{17,20}', content)
        target_id = None
        for cid in all_ids:
            if int(cid) != bot.user.id:
                target_id = int(cid)
                break

        if target_id:
            bot.target_room = target_id 
            try:
                channel = bot.get_channel(target_id)
                if not channel:
                    channel = await bot.fetch_channel(target_id)
                
                if not isinstance(channel, discord.VoiceChannel):
                    await message.channel.send("id nay k phai voice channel")
                    return     
                if message.guild.voice_client:
                    await message.guild.voice_client.disconnect(force=True)
                await channel.connect(self_deaf=True, self_mute=True)                      
                try:
                    await message.guild.me.edit(mute=True, deafen=True)
                except:
                    print("Thiếu quyền Mute/Deafen trên server")

                await message.channel.send("da chui vao treo (Server Muted/Deafened)")

            except Exception as e:
                print(f"loi: {e}")
                await message.channel.send("loi k vao dc")
        else:
            await message.channel.send("tag r vut cai id room vao")
            
    await bot.process_commands(message)

@tasks.loop(seconds=20)
async def auto_reconnect():
    if not bot.target_room: return
    channel = bot.get_channel(bot.target_room)
    if not channel: return
    vc = channel.guild.voice_client
    if not vc or not vc.is_connected():
        try:
            await channel.connect(self_deaf=True, self_mute=True)
            await channel.guild.me.edit(mute=True, deafen=True)
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
        
      
        await channel.connect(self_deaf=True, self_mute=True)
        try:
            await interaction.guild.me.edit(mute=True, deafen=True)
        except:
            pass

        await interaction.response.send_message(f"da treo tai {channel.name}")
    except:
        await interaction.response.send_message("id loi ", ephemeral=True)

@bot.tree.command(name="limit", description="set gioi han nguoi vao vc")
async def set_limit(interaction: discord.Interaction, limit: int):
    if not interaction.user.voice:
        return await interaction.response.send_message("get in room to set", ephemeral=True)
    
    channel = interaction.user.voice.channel
    await channel.edit(user_limit=limit)
    await interaction.response.send_message(f"da set limit room {channel.name} la {limit}")

@bot.tree.command(name="lock", description="lock vc")
async def lock_vc(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("get in vc first", ephemeral=True)
    
    channel = interaction.user.voice.channel
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    overwrite.view_channel = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"lock room {channel.name}")

@bot.tree.command(name="allow", description="allow user")
async def allow(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.voice:
        return await interaction.response.send_message("vô room đi cha", ephemeral=True)
    
    channel = interaction.user.voice.channel
    await channel.set_permissions(member, view_channel=True, connect=True, send_messages=True)
    await interaction.response.send_message(f"da mo quyen cho {member.display_name}")

@bot.tree.command(name="remove_allow", description="remove user allowance")
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
