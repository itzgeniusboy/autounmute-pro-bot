import asyncio
import time
import sys
import subprocess

# 🚀 डिपेंडेंसी चेक और ऑटो-इंस्टॉल
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
except ImportError:
    print("📥 Pyrogram or dependencies missing! Installing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 क्रेडेंशियल्स [As per image_3.png]
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# एक्टिव चैट ट्रैकर (बॉट जिन ग्रुप/चैनल में ऐड होगा, उन्हें यहाँ ट्रैक करेगा)
active_chats = set()
already_joined_users = set()

# 🤖 /start कमांड
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add to Telegram Group 👥", url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages")],
        [InlineKeyboardButton(text="➕ Add to Telegram Channel 📢", url=f"https://t.me/{bot_username}?startchannel=true&admin=manage_video_chats+invite_users+delete_messages")]
    ])

    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE v2** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Active & Monitoring` 🟢\n"
        "» **Core:** `Interval Scanning Architecture` 📡\n\n"
        "⚙️ **Easy Setup:**\n"
        "Add me using the buttons below, give admin rights, and type `/monitor` in your group/channel to activate the automated scanning shield."
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# 📡 /monitor कमांड (यह कमांड बॉट को बैकग्राउंड स्कैनर में रजिस्टर कर देगी)
@app.on_message(filters.command("monitor") & (filters.group | filters.channel))
async def register_chat(client, message):
    chat_id = message.chat.id
    active_chats.add(chat_id)
    await message.reply_text("🚀 **Aura Shield Activated!** Bot is now actively monitoring this voice chat room 24x7.")

# 🔄 [THE UNLIMITED OVERDRIVE LOOP] - हर 1.5 सेकंड में सबको स्कैन करके ऑटो-अनम्यूट करने वाला कोर
async def voice_chat_scanner():
    while True:
        await asyncio.sleep(1.5) # स्कैनिंग इंटरवल
        for chat_id in list(active_chats):
            try:
                chat_peer = await app.resolve_peer(chat_id)
                full_chat = await app.invoke(functions.channels.GetFullChannel(channel=chat_peer))
                group_call = full_chat.full_chat.call
                
                if not group_call:
                    continue # अगर VC बंद है तो स्किप करें

                # कॉल के मेंबर्स फ़ेच करना
                participants = await app.invoke(
                    functions.phone.GetGroupCallParticipants(call=group_call, ids=[], sources=[], offset="", limit=100)
                )
                
                for participant in participants.participants:
                    u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                    if not u_id:
                        continue

                    # 🛑 FIRST JOIN UNMUTE LOGIC
                    if u_id not in already_joined_users:
                        already_joined_users.add(u_id)
                        if participant.muted:
                            await app.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))
                        continue

                    # 🛑 RAISE HAND UNMUTE LOGIC
                    if participant.raise_hand_rating and participant.muted:
                        await app.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await app.resolve_peer(u_id), muted=False))
                        
            except Exception as e:
                print(f"Scanner exception for chat {chat_id}: {e}")

# 📢 /unmuteall कमांड
@app.on_message(filters.command("unmuteall") & (filters.group | filters.channel))
async def unmute_all_participants(client, message):
    chat_id = message.chat.id
    status = await message.reply_text("⚡ `Force syncing voice architecture...` ⚡")
    
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
                    await client.invoke(functions.phone.EditGroupCallParticipant(call=group_call, peer=await client.resolve_peer(u_id), muted=False))
                    unmuted_count += 1
        
        await status.edit(f"🔥 **CORE RESET SUCCESSFUL**\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n» **Cleared Users:** `{unmuted_count}` participants are now live! 🎙️")
    except Exception as e:
        await status.edit(f"❌ **System Exception:** `{str(e)}`")

# बैकग्राउंड टास्क स्टार्ट करने का लॉजिक
async def main():
    await app.start()
    print("🚀 AutoUnmute Scanner Core Active...")
    await voice_chat_scanner()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
