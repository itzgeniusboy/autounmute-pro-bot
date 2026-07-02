import asyncio
import time
import sys
import subprocess

# 🚀 डिपेंडेंसी चेक और ऑटो-इंस्टॉल
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
except ImportError:
    print("📥 Pyrogram or dependencies missing! Installing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types

# 🔑 आपके क्रेडेंशियल्स
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🧠 मेमोरी शेड: उन यूज़र्स को ट्रैक करने के लिए जो पहले ही कॉल ज्वाइन कर चुके हैं
# इससे यह कन्फर्म होगा कि ऑटो-अनम्यूट सिर्फ "First Join" पर काम करे
already_joined_users = set()

# 🤖 /start कमांड (Premium Aesthetic Look)
@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    welcome_msg = (
        "⚡ **AUTO-UNMUTE PRO ENGINE** ⚡\n"
        "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        "» **Status:** `Operational 24x7` 🟢\n"
        "» **Core:** `Pyrogram Daemon Architecture` 📡\n\n"
        "⚙️ **How to Setup:**\n"
        "1️⃣ Add me to your **Channel** or **Group**.\n"
        "2️⃣ Grant me Admin rights with **'Manage Video Chats'** (or *Invite Users*) permissions.\n\n"
        "📊 **Available Commands:**\n"
        "🔹 `/unmuteall` — Force unmute all active hand-raisers instantly."
    )
    await message.reply_text(welcome_msg)

# 🔥 [SMART AUTO-UNMUTE NODE] 
@app.on_raw_update()
async def handle_voice_chat_updates(client, update, users, chats):
    if isinstance(update, types.UpdateGroupCallParticipants):
        for participant in update.participants:
            # यूज़र या चैनल आईडी निकालें
            u_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
            
            if not u_id:
                continue

            # 🛑 [FIRST JOIN LOGIC] 
            # अगर यूज़र लिस्ट में नहीं है, मतलब उसने अभी-अभी कॉल जॉइन की है
            if u_id not in already_joined_users:
                already_joined_users.add(u_id) # उसे मेमोरी में सेव कर लो
                
                # अगर वह म्यूटेड जॉइन हुआ है, तो उसे तुरंत अनम्यूट करो
                if participant.muted:
                    try:
                        await client.invoke(
                            functions.phone.EditGroupCallParticipant(
                                call=update.call,
                                peer=await client.resolve_peer(u_id),
                                muted=False # Unmute instantly on first join
                            )
                        )
                        print(f"✅ Instant Unmuted on First Join — ID: {u_id}")
                    except Exception as e:
                        print(f"❌ First join unmute failed: {e}")
                continue

            # 🛑 [ADMIN PROTECTION LOGIC]
            # अगर यूजर पहले से कॉल पर है और उसने 'Raise Hand' किया है, तभी अनम्यूट होगा
            # अगर एडमिन ने उसे म्यूट कर दिया है और उसने हाथ नहीं उठाया, तो बॉट उसे म्यूट ही रहने देगा
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

# 📢 /unmuteall कमांड (Premium UI Response)
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
    print("🚀 Premium AutoUnmute Pro Engine Started...")
    app.run()
