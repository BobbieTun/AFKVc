import discord
from discord.ext import commands, tasks
import re
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "ok", 200
def run_flask(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run_flask, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="~", intents=intents)
bot.target_room = None
MY_ID = 554188744068956171

@bot.event
async def on_ready():
    if not auto_reconnect.is_running(): auto_reconnect.start()

@bot.event
async def on_message(msg):
    if msg.author == bot.user or msg.author.id != MY_ID: return
    
    if bot.user.mentioned_in(msg):
        cnt = msg.content.strip().lower()
        if "leave" in cnt:
            if msg.guild.voice_client:
                bot.target_room = None 
                await msg.guild.voice_client.disconnect()
                await msg.channel.send("left")
            return
            
        ids = re.findall(r'\d{17,20}', cnt)
        tid = next((int(i) for i in ids if int(i) != bot.user.id), None)

        if tid:
            bot.target_room = tid 
            try:
                ch = bot.get_channel(tid) or await bot.fetch_channel(tid)
                if not isinstance(ch, discord.VoiceChannel): return
                if msg.guild.voice_client: await msg.guild.voice_client.disconnect(force=True)
                await ch.connect(self_deaf=True, self_mute=True)                      
                try: await msg.guild.me.edit(mute=True, deafen=True)
                except: pass
                await msg.channel.send("joined")
            except: await msg.channel.send("err")
            
    await bot.process_commands(msg)

@tasks.loop(seconds=20)
async def auto_reconnect():
    if not bot.target_room: return
    ch = bot.get_channel(bot.target_room)
    if not ch: return
    vc = ch.guild.voice_client
    if not vc or not vc.is_connected():
        try:
            await ch.connect(self_deaf=True, self_mute=True)
            await ch.guild.me.edit(mute=True, deafen=True)
        except: pass

@bot.command()
async def join(ctx, rid: str):
    if ctx.author.id != MY_ID: return
    try:
        ch = bot.get_channel(int(rid)) or await bot.fetch_channel(int(rid))
        if not isinstance(ch, discord.VoiceChannel): return
        bot.target_room = int(rid)
        if ctx.guild.voice_client: await ctx.guild.voice_client.disconnect(force=True)
        await ch.connect(self_deaf=True, self_mute=True)
        try: await ctx.guild.me.edit(mute=True, deafen=True)
        except: pass
        await ctx.send("joined")
    except: await ctx.send("err")

@bot.command()
async def limit(ctx, lim: int):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        await ctx.author.voice.channel.edit(user_limit=lim)
        await ctx.send("done")
    except: await ctx.send("thieu quyen manage channels")

@bot.command()
async def unlimit(ctx):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        await ctx.author.voice.channel.edit(user_limit=0)
        await ctx.send("unlimited")
    except: await ctx.send("thieu quyen manage channels")

@bot.command()
async def lock(ctx):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        ch = ctx.author.voice.channel
        ow = ch.overwrites_for(ctx.guild.default_role)
        ow.connect = ow.view_channel = False
        await ch.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send("locked")
    except: await ctx.send("thieu quyen manage channels/roles")

@bot.command()
async def unlock(ctx):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        ch = ctx.author.voice.channel
        ow = ch.overwrites_for(ctx.guild.default_role)
        ow.connect = ow.view_channel = None
        await ch.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send("unlocked")
    except: await ctx.send("thieu quyen manage channels/roles")

@bot.command()
async def allow(ctx, mem: discord.Member):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        await ctx.author.voice.channel.set_permissions(mem, view_channel=True, connect=True, send_messages=True)
        await ctx.send("allowed")
    except: await ctx.send("thieu quyen manage channels/roles")

@bot.command()
async def remove_allow(ctx, mem: discord.Member):
    if ctx.author.id != MY_ID: return
    if not ctx.author.voice: return await ctx.send("ong phai vao voice truoc")
    try:
        await ctx.author.voice.channel.set_permissions(mem, overwrite=None)
        await ctx.send("removed")
    except: await ctx.send("thieu quyen manage channels/roles")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('tokens'))
