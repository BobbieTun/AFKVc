import discord
from discord.ext import commands, tasks
import re
import os
import aiohttp
from datetime import datetime
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

# config mac dinh la gui DM cho id cua ong
bot.log_conf = {'type': 'dm', 'val': MY_ID} 
bot.join_time = None

async def send_log(g_name, c_name):
    if not bot.join_time: return
    delta = datetime.now() - bot.join_time
    bot.join_time = None 
    
    h, r = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(r, 60)
    
    eb = discord.Embed(title="🔴 Bot Rớt / Out VC", color=0xff0000)
    eb.add_field(name="Server", value=g_name, inline=True)
    eb.add_field(name="Room", value=c_name, inline=True)
    eb.add_field(name="Time Treo", value=f"{h}h {m}m {s}s", inline=False)
    eb.timestamp = datetime.now()
    
    try:
        if bot.log_conf['type'] == 'dm':
            u = await bot.fetch_user(bot.log_conf['val'])
            await u.send(embed=eb)
        elif bot.log_conf['type'] == 'web':
            async with aiohttp.ClientSession() as ses:
                wh = discord.Webhook.from_url(bot.log_conf['val'], session=ses)
                await wh.send(embed=eb)
    except: pass

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
                await send_log(msg.guild.name, msg.guild.voice_client.channel.name)
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
                
                if msg.guild.voice_client: 
                    await send_log(msg.guild.name, msg.guild.voice_client.channel.name)
                    await msg.guild.voice_client.disconnect(force=True)
                
                await ch.connect(self_deaf=True, self_mute=True)
                bot.join_time = datetime.now()
                                      
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
        await send_log(ch.guild.name, ch.name)
        try:
            await ch.connect(self_deaf=True, self_mute=True)
            await ch.guild.me.edit(mute=True, deafen=True)
            bot.join_time = datetime.now()
        except: pass

@bot.command()
async def join(ctx, rid: str):
    if ctx.author.id != MY_ID: return
    try:
        ch = bot.get_channel(int(rid)) or await bot.fetch_channel(int(rid))
        if not isinstance(ch, discord.VoiceChannel): return
        bot.target_room = int(rid)
        
        if ctx.guild.voice_client: 
            await send_log(ctx.guild.name, ctx.guild.voice_client.channel.name)
            await ctx.guild.voice_client.disconnect(force=True)
            
        await ch.connect(self_deaf=True, self_mute=True)
        bot.join_time = datetime.now()
        
        try: await ctx.guild.me.edit(mute=True, deafen=True)
        except: pass
        await ctx.send("joined")
    except: await ctx.send("err")

@bot.command()
async def timecheck(ctx):
    if ctx.author.id != MY_ID: return
    if not bot.join_time: return await ctx.send("chua vao room")
    d = datetime.now() - bot.join_time
    h, r = divmod(int(d.total_seconds()), 3600)
    m, s = divmod(r, 60)
    await ctx.send(f"treo dc: {h}h {m}m {s}s")

@bot.command()
async def configlog(ctx, typ: str, val: str):
    if ctx.author.id != MY_ID: return
    if typ not in ['dm', 'web']: return await ctx.send("type phai la 'dm' hoac 'web'")
    
    if typ == 'dm':
        uid = re.sub(r'\D', '', val)
        if not uid: return await ctx.send("loi id")
        bot.log_conf = {'type': 'dm', 'val': int(uid)}
    else:
        bot.log_conf = {'type': 'web', 'val': val}
    await ctx.send("luu config ok")

@bot.command()
async def limit(ctx, lim: int):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        await ctx.author.voice.channel.edit(user_limit=lim)
        await ctx.send("done")
    except: pass

@bot.command()
async def unlimit(ctx):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        await ctx.author.voice.channel.edit(user_limit=0)
        await ctx.send("unlimited")
    except: pass

@bot.command()
async def lock(ctx):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        ch = ctx.author.voice.channel
        ow = ch.overwrites_for(ctx.guild.default_role)
        ow.connect = ow.view_channel = False
        await ch.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send("locked")
    except: pass

@bot.command()
async def unlock(ctx):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        ch = ctx.author.voice.channel
        ow = ch.overwrites_for(ctx.guild.default_role)
        ow.connect = ow.view_channel = None
        await ch.set_permissions(ctx.guild.default_role, overwrite=ow)
        await ctx.send("unlocked")
    except: pass

@bot.command()
async def allow(ctx, mem: discord.Member):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        await ctx.author.voice.channel.set_permissions(mem, view_channel=True, connect=True, send_messages=True)
        await ctx.send("allowed")
    except: pass

@bot.command()
async def remove_allow(ctx, mem: discord.Member):
    if ctx.author.id != MY_ID or not ctx.author.voice: return
    try:
        await ctx.author.voice.channel.set_permissions(mem, overwrite=None)
        await ctx.send("removed")
    except: pass

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('tokens'))
