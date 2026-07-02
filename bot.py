import asyncio
import time
import sys
import subprocess

# 🚀 Dependency check and auto-installer
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait
except ImportError:
    print("📥 Pyrogram missing! Installing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from pyrogram.errors import FloodWait

# 🔑 Credentials
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Memory allocations for auto-discovery
monitored_chats = set()
already_joined_users = set()

# 🤖 /start command handler (Premium UI)
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add to Telegram Group 👥", url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages")],
        [InlineKeyboardButton(text="➕ Add to Telegram Channel 📢", url=f"https://t.me/{bot_username}?startchannel=true&admin=manage_video_chats+invite_users+delete_messages")]
    ])

    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE v3** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Fully Automated (Zero-Command Mode)` 🟢\n"
        "» **Core:** `Auto-Discovery Scanner Engine` 📡\n\n"
        "⚙️ **Zero Setup Required:**\n"
        "Simply add me to your Group or Channel as an Admin. The shield activates **instantly and automatically** without any commands! \n\n"
        "📊 **Bulk Command:**\n"
        "🔹 `/unmuteall` — Manual overdrive to unmute everyone at once."
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# 🔍 [SMART AUTO-DISCOVERY NODE]
@app.on_message(filters.group | filters.channel)
async def auto_discover_chats(client, message):
    chat_id = message.chat.id
    if chat_id not in monitored_chats:
        monitored_chats.add(chat_id)
        print(f"📡 [Auto-Discovered] Connected to Chat ID: {chat_id}")

# 🔄 [THE UNLIMITED AUTOMATIC LOOP]
async def fully_automatic_scanner():
    print("🤖 Fully Auto Scanner Loop Initiated...")
    while True:
        await asyncio.sleep(1.0) # 1-second rapid scanning interval
        
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

                    # 🔥 First join automation
                    if u_id not in already_joined_users:
                        already_joined_users.add(u_id)
                        if participant.muted:
                            await app.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))
                            print(f"⚡ [Auto-Unmuted] First Join -> User: {u_id}")
                        continue

                    # 🔥 Raise Hand tracking
                    if participant.raise_hand_rating and participant.muted:
                        await app.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))
                        print(f"⚡ [Auto-Unmuted] Raised Hand -> User: {u_id}")
                        
            except FloodWait as e:
                print(f"⚠️ Internal Loop Warning: Sleeping for {e.value}s due to Telegram constraints.")
                await asyncio.sleep(e.value)
            except Exception as e:
                pass

# 📢 /unmuteall command (Emergency Overdrive)
@app.on_message(filters.command("unmuteall") & (filters.group | filters.channel))
async def unmute_all_participants(client, message):
    chat_id = message.chat.id
    status = await message.reply_text("⚡ `Force syncing voice infrastructure...` ⚡")
    
    try:
        chat_peer = await client.resolve_peer(chat_id)
        full_chat = await client.invoke(functions.channels.GetFullChannel(channel=chat_peer))
        group_call = full_chat.full_chat.call
        
        if not group_call:
            await status.edit("⚠️ **Matrix Error:** No active Voice Chat detected.")
            return

        participants = await client.invoke(functions.phone.GetGroupCallParticipants(call=group_call, ids=[], sources=[], offset="", limit=100))
        unmuted_count = 0
        
        for participant in participants.participants:
            if participant.muted:
                u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                if u_id:
                    await client.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))
                    unmuted_count += 1
        
        await status.edit(f"🔥 **CORE RESET SUCCESSFUL**\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n» **Cleared Users:** `{unmuted_count}` participants are now live! 🎙️")
    except FloodWait as e:
        await status.edit(f"⚠️ **FloodWait Active:** Rate limited by Telegram. Retrying in {e.value} seconds.")
    except Exception as e:
        await status.edit(f"❌ **System Exception:** `{str(e)}`")

# Startup architecture with FloodWait handling configuration
async def main():
    try:
        await app.start()
        print("🚀 Zero-Command Automation Core Online...")
        await fully_automatic_scanner()
    except FloodWait as e:
        print(f"🛑 [CRITICAL WARNING] Telegram FloodWait hit! Server requires a wait of {e.value} seconds.")
        print(f"Fixing automatically: Holding process execution for {e.value + 5} seconds...")
        await asyncio.sleep(e.value + 5)
        # Attempt recovery reconnect
        await app.start()
        await fully_automatic_scanner()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
