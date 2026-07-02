import asyncio
import sys
import subprocess
import os
import time

# 🚀 Highly Stable Dependency Management Layer
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pytgcalls import PyTgCalls
    from pytgcalls.types import AudioPiped
    from gtts import gTTS
except ImportError:
    print("📥 Bootstrapping stable production-ready audio nodes...")
    # Using 2.1.0 which is explicitly supported and available on PyPI
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5", "pytgcalls==2.1.0", "yt-dlp", "gTTS"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pytgcalls import PyTgCalls
    from pytgcalls.types import AudioPiped
    from gtts import gTTS

# 🔑 Credentials Configuration
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8180911405:AAH7fAPgA-hBcsMv2rc3s0PMUV4bNwBsAvE"

app = Client("sound_engine_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=4)
call_client = PyTgCalls(app)

monitored_chats = set()
current_active_stream = {}

# 🤖 /start Command UI Layout
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add to Telegram Group 👥", url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages")],
        [InlineKeyboardButton(text="➕ Add to Telegram Channel 📢", url=f"https://t.me/{bot_username}?startchannel=true&admin=manage_video_chats+invite_users+delete_messages")]
    ])
    welcome_msg = (
        "🎵 **ONE-CORE SOUND ENGINE** 🎵\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Engine Status:** `Operational` 🟢\n"
        "» **Ad-Policy:** `100% Pure Ad-Free Transmission` 🛡️\n"
        "» **Features:** `Auto-Unmute & Ambient Voice Greetings` 📡\n\n"
        "📊 **Control Command Layout:**\n"
        "🔹 `/play <song name>` — Search and stream any song instantly from YouTube.\n"
        "🔹 `/stop` — Terminate the active voice call audio processing."
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# Auto-Discovery Tracker Module
@app.on_message(filters.group | filters.channel)
async def auto_discover(client, message):
    chat_id = message.chat.id
    if chat_id not in monitored_chats:
        monitored_chats.add(chat_id)

# 🎙️ Ambient Welcome Greetings Processing
async def trigger_voice_welcome(chat_id, user_name):
    try:
        welcome_text = f"Welcome to the live stream, {user_name}! Enjoy the ad free experience."
        tts = gTTS(text=welcome_text, lang='en')
        tts.save("welcome.mp3")
        
        await call_client.change_stream(chat_id, AudioPiped("welcome.mp3"))
        await asyncio.sleep(4)
        
        if chat_id in current_active_stream:
            await call_client.change_stream(chat_id, AudioPiped(current_active_stream[chat_id]))
            
        os.remove("welcome.mp3")
    except Exception:
        pass

# 🔄 Asynchronous Auto-Unmute & Scan Radar Loop
async def active_ambient_radar():
    already_checked_users = set()
    while True:
        await asyncio.sleep(2.0)
        for chat_id in list(monitored_chats):
            try:
                chat_peer = await app.resolve_peer(chat_id)
                full_chat = await app.invoke(functions.channels.GetFullChannel(channel=chat_peer))
                group_call = full_chat.full_chat.call
                
                if not group_call:
                    continue

                participants = await app.invoke(
                    functions.phone.GetGroupCallParticipants(call=group_call, ids=[], sources=[], offset="", limit=100)
                )
                
                for participant in participants.participants:
                    u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                    if not u_id:
                        continue

                    if participant.muted:
                        await app.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))

                    if u_id not in already_checked_users:
                        already_checked_users.add(u_id)
                        user_data = await app.get_users(u_id)
                        first_name = user_data.first_name if user_data.first_name else "User"
                        asyncio.create_task(trigger_voice_welcome(chat_id, first_name))
                        
            except Exception:
                pass

# 🎵 YouTube Search & Audio Ingestion Node (Ad-Free)
@app.on_message(filters.command("play") & (filters.group | filters.channel))
async def play_audio(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Format:** `/play <song name>`")
        return

    query = message.text.split(None, 1)[1]
    status = await message.reply_text("🔍 `Searching YouTube server nodes...` ⚡")
    
    try:
        import yt_dlp
        ydl_opts = {'format': 'bestaudio', 'quiet': True, 'default_search': 'ytsearch'}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                url = info['entries'][0]['url']
                title = info['entries'][0]['title']
            else:
                await status.edit("❌ **Search Error:** No matching audio files found.")
                return

        current_active_stream[chat_id] = url
        try:
            await call_client.join_group_call(chat_id, AudioPiped(url))
        except Exception:
            await call_client.change_stream(chat_id, AudioPiped(url))
            
        await status.edit(f"🎶 **Streaming Ad-Free Audio Node!**\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n» **Playing:** `{title}`")
    except Exception as e:
        await status.edit(f"❌ **Failed to establish pipe connection:** `{str(e)}`")

@app.on_message(filters.command("stop") & (filters.group | filters.channel))
async def stop_audio(client, message):
    chat_id = message.chat.id
    try:
        await call_client.leave_group_call(chat_id)
        current_active_stream.pop(chat_id, None)
        await message.reply_text("🛑 **Stream Disconnected Successfully.**")
    except Exception:
        pass

# ⚙️ Clean Execution & Wrapper Node Integration
def run_safely():
    while True:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(active_ambient_radar())
            app.run()
            break 
        except Exception as error:
            print(f"⚠️ Initializing restart sequence due to unexpected break: {error}")
            time.sleep(5)

if __name__ == "__main__":
    run_safely()
