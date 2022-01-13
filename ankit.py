import os
import random
import time
import logging
import requests
import aiohttp
import json
from youtube_dl import YoutubeDL
from pyrogram import filters, Client, idle
from youtubesearchpython import SearchVideos
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from config import API_ID, API_HASH, BOT_TOKEN


# logging
bot = Client(
   "Song Downloader",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)


@bot.on_message(filters.command("start") & ~filters.edited)
async def start(_, message):
   if message.chat.type == 'private':
       await message.reply("**Hey There, I'm a song downloader bot.\nUsage:** `/song [query]`",   
                            reply_markup=InlineKeyboardMarkup(
                                [[
                                     InlineKeyboardButton(
                                            "🔰Developer🔰", url="https://github.com/LEGEND-ANKIT")
                                    ]]
                            ))
   else:
      await message.reply("**Song Downloader Bot is Online ✨**")



@bot.on_message(filters.command("song") & ~filters.edited)
async def song(_, message):
    if len(message.command) < 2:
       return await message.reply("**Usage:**\n - `/song [query]`")
    query = message.text.split(None, 1)[1]
    user_name = message.from_user.first_name
    shed = await message.reply("🔎 Finding the Song...")
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": False,
        "logtostderr": False,
    }
    try:
        search = SearchVideos(query, offset=1, mode="json", max_results=1)
        test = search.result()
        p = json.loads(test)
        q = p.get("search_result")
        url = q[0]["link"]

    except Exception as e:
        await shed.edit(
            "❌ Found Nothing.\nTry another keyword or maybe spell it properly."
        )
        print(str(e))
        return
    await shed.edit("📥 Downloading...")
    try:
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
            rip_file = rip.prepare_filename(rip_data)
            
        dir = os.listdir()
        if f"{rip_data['id']}.mp3.jpg" in dir:
            thumb = f"{rip_data['id']}.mp3.jpg"
        elif f"{rip_data['id']}.mp3.webp" in dir:
            thumb = f"{rip_data['id']}.mp3.webp"
        else:
            thumb = None
        tail = time.time()
        CAPT = f"**🎶 Song -** [{rip_data['title']}]({url}) \n**👤 Req. By -** `{user_name}` \n"
        s = await message.reply_audio(rip_file, caption=CAPT, thumb=thumb, parse_mode='md', title=str(rip_data["title"]), duration=int(rip_data["duration"]))
        await shed.delete()
    except Exception as e:
        await shed.edit("❌ Error")
        print(e)

    try:
        os.remove(f"{rip_data['id']}.mp3")
        os.remove(thumb)
    except Exception as e:
        print(e)

bot.start()
idle()
