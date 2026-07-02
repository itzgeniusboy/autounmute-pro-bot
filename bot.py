import asyncio
import time
import sys
import subprocess

# 🚀 डिपेंडेंसी चेक और ऑटो-इंस्टॉल
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat
except ImportError:
    print("📥 Pyrogram or dependencies missing! Installing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat

# 🔑 क्रेडेंशियल्स
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
# 🎯 आपका नया अपडेटेड टोकन
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# मेमोरी शेड: फर्स्ट जॉइन ट्रैक करने के लिए
already_joined_users = set()

# 🤖 /start कमांड (Aesthetic UI with Add Bot Button)
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_username = (await client.get_me()).username
    
    # 🔥 [PREMIUM CHAT SELECTOR BUTTON]
    # यह बटन सीधे ग्रुप/चैनल सेलेक्ट करने और एडमिन परमिशन मांगने का पॉपअप खोलेगा
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="➕ Add Bot to Group / Channel ➕",
                url=f"https://t.me/{bot_username}?startgroup=true&admin=manage_video_chats+invite_users+delete_messages"
            )
        ]
    ])

    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Operational 24x7` 🟢\n"
        "» **Core:** `Pyrogram Daemon Architecture` 📡\n\n"
        "⚙️ **Easy Setup:**\n"
        "Click the premium button below, select your Group or Channel, and simply **Allow/Add as Admin**. The required video chat privileges are pre-configured! \n\n"
        "📊 **Available Commands:**\n"
        "🔹 `/unmuteall` — Force unmute all active hand-raisers instantly."
    )
    await message.reply_text(welcome_msg, reply_markup=markup)

# 🔥 [SMART AUTO-UNMUTE NODE]
@app.on_raw_update()
async def handle_voice_chat_updates(client, update, users, chats):
    if isinstance(update, types.UpdateGroupCallParticipants):
        for participant in update.participants:
            u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
            
            if not u_id:
                continue

            # 🛑 [FIRST JOIN LOGIC]
            if u_id not in already_joined_users:
                already_joined_users.add(u_id)
                
                if participant.muted:
                    try:
                        await client.invoke(
                            functions.phone.EditGroupCallParticipant(
                                call=update.call,
                                peer=await client.resolve_peer(u_id),
                                muted=False
                            )
                        )
                        print(f"✅ Instant Unmuted on First Join — ID: {u_id}")
                    except Exception as e:
                        print(f"❌ First join unmute failed: {e}")
                continue

            # 🛑 [ADMIN PROTECTION LOGIC - RAISE HAND]
            if participant.raise_hand_rating and participant.muted:
                try:
                    await client.invoke(
                        functions.phone.EditGroupCallParticipant(
                            call=update.call,
                            peer=await client.resolve_peer(u_id),
                            muted=False
                        )
                    )
                    print(f"✅ Unmuted via Raise Hand — ID: {u_id}")
                except Exception as e:
                    print(f"❌ Raise hand unmute failed: {e}")

# 📢 /unmuteall कमांड
@app.on_message(filters.command("unmuteall") & (filters.group | filters.channel))
async def unmute_all_participants(client, message):
    chat_id = message.chat.id
    status = await message.reply_text("⚡ `Syncing with voice infrastructure, please wait...` ⚡")
    
    try:
        chat_peer = await client.resolve_peer(chat_id)
        full_chat = await client.invoke(functions.channels.GetFullChannel(channel=chat_peer))
        group_call = full_chat.full_chat.call
        
        if not group_call:
            await status.edit("⚠️ **Matrix Error:** No active Voice Chat detected in this chat/channel.")
            return

        participants = await client.invoke(
            functions.phone.GetGroupCallParticipants(call=group_call, ids=[], sources=[], offset="", limit=100)
        )
        
        unmuted_count = 0
        for participant in participants.participants:
            if participant.muted:
                u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                
                if u_id:
                    await client.invoke(
                        functions.phone.EditGroupCallParticipant(
                            call=group_call,
                            peer=await client.resolve_peer(u_id),
                            muted=False
                        )
                    )
                    unmuted_count += 1
        
        await status.edit(
            f"🔥 **CORE RESET SUCCESSFUL** 🔥\n"
            f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
            f"» **Action:** Bulk Overdrive Unmute\n"
            f"» **Cleared Users:** `{unmuted_count}` participants are now live! 🎙️"
        )
        
    except Exception as e:
        await status.edit(f"❌ **System Exception:** `{str(e)}` \n\n*Make sure I am an Admin with Voice Chat privileges.*")

if __name__ == "__main__":
    print("🚀 Premium AutoUnmute Pro Engine with Chat Selector Started...")
    app.run()
