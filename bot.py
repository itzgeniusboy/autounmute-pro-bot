import asyncio
import sys
import subprocess
import time

# 🚀 Automated Dependency Management
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait
except ImportError:
    print("📥 Installing missing framework dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait

# 🔑 Credentials Configuration
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client(
    "voice_bot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    workers=2
)

# 🤖 Private /start Command Interface
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add to Telegram Group 👥", url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages")],
        [InlineKeyboardButton(text="➕ Add to Telegram Channel 📢", url=f"https://t.me/{bot_username}?startchannel=true&admin=manage_video_chats+invite_users+delete_messages")]
    ])

    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE v4** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Active Cloud Synchronization` 🟢\n"
        "» **Core:** `External Platform Daemon Mode` 📡\n\n"
        "⚙️ **Zero Setup Required:**\n"
        "Simply add me to your Group or Channel using the buttons below as an Admin. The engine integrates with your chat layout immediately!\n\n"
        "📊 **Bulk Overdrive:**\n"
        "🔹 `/unmuteall` — Force open all microphone states manually."
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# 🔥 [REAL-TIME EVENT SHIELD]
@app.on_raw_update()
async def handle_voice_chat_raw(client, update, users, chats):
    if isinstance(update, types.UpdateGroupCallParticipants):
        for participant in update.participants:
            u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
            if not u_id:
                continue

            if participant.muted:
                try:
                    await client.invoke(
                        functions.phone.EditGroupCallParticipant(
                            call=update.call,
                            peer=await client.resolve_peer(u_id),
                            muted=False
                        )
                    )
                    print(f"✅ Shield Verified: Granted Mic Access -> ID: {u_id}")
                except Exception:
                    pass

# 📢 Manual Backup Overdrive Command
@app.on_message(filters.command("unmuteall") & (filters.group | filters.channel))
async def unmute_all_participants(client, message):
    chat_id = message.chat.id
    try:
        chat_peer = await client.resolve_peer(chat_id)
        full_chat = await client.invoke(functions.channels.GetFullChannel(channel=chat_peer))
        group_call = full_chat.full_chat.call
        
        if not group_call:
            await message.reply_text("⚠️ **Matrix Error:** No active Voice Chat found.")
            return

        participants = await client.invoke(functions.phone.GetGroupCallParticipants(call=group_call, ids=[], sources=[], offset="", limit=100))
        
        for participant in participants.participants:
            if participant.muted:
                u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                if u_id:
                    await client.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await client.resolve_peer(u_id), muted=False))
                    
        await message.reply_text("🔥 **Core Reset Successful:** Everyone unmuted!")
    except Exception as e:
        await message.reply_text(f"❌ **System Exception:** `{str(e)}`")

# ⚡ [SAFE RUN TIME WRAPPER]
def run_safely():
    while True:
        try:
            print("🚀 Initializing Handshake with Telegram API Clusters...")
            app.run()
            break # Exit loop gracefully if execution wraps normally
        except FloodWait as e:
            print(f"🛑 [FLOOD WAIT ACTIVATED] Telegram rate limit detected. Code: {e.value} seconds.")
            print(f"System Action: Suspending execution safely for {e.value + 5}s to reset backend thresholds...")
            time.sleep(e.value + 5)
            print("🔄 Cooldown sequence cleared. Retrying system authorization node...")
        except Exception as crash:
            print(f"❌ Unhandled engine exception: {crash}")
            break

if __name__ == "__main__":
    run_safely()
