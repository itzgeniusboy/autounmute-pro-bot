import asyncio
import sys
import subprocess
import time

try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait

API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=4)

monitored_chats = set()

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add to Telegram Group 👥", url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages")],
        [InlineKeyboardButton(text="➕ Add to Telegram Channel 📢", url=f"https://t.me/{bot_username}?startchannel=true&admin=manage_video_chats+invite_users+delete_messages")]
    ])
    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE v5** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Channel & Group Auto-Scanner Active` 🟢\n"
        "» **Core:** `Hybrid Loop-Interval Architecture` 📡\n\n"
        "⚙️ **Zero Setup Required:**\n"
        "Add me as Admin, post ONE message in the channel, and turn on the Live Stream!"
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# ऑटो-डिटेक्शन: चैनल का कोई भी मैसेज आते ही एक्टिवेट होगा
@app.on_message(filters.group | filters.channel)
async def auto_discover_chats(client, message):
    chat_id = message.chat.id
    if chat_id not in monitored_chats:
        monitored_chats.add(chat_id)
        print(f"📡 [Auto-Discovered] Connected to Channel/Group ID: {chat_id}")

async def passive_channel_radar():
    print("🤖 Automated Channel Scanner Thread Initiated...")
    while True:
        await asyncio.sleep(2.0) # 2 सेकंड का फ़ास्ट स्कैनिंग इंटरवल
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
                    if participant.muted:
                        u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                        if not u_id:
                            continue
                        
                        # डायरेक्ट क्लाउड अनम्यूट कमांड
                        await app.invoke(
                            functions.phone.EditGroupCallParticipant(
                                call=group_call, 
                                peer=await app.resolve_peer(u_id), 
                                muted=False
                            )
                        )
                        print(f"⚡ [Radar] Unmuted Participant -> ID: {u_id}")
                        
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                pass

def run_safely():
    while True:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(passive_channel_radar())
            app.run()
            break 
        except FloodWait as e:
            time.sleep(e.value + 5)
        except Exception:
            break

if __name__ == "__main__":
    run_safely()
