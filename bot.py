import asyncio
import time
import sys
import subprocess

# 🚀 डिपेंडेंसी चेक और ऑटो-इंस्टॉल आर्किटेक्चर
try:
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types
except ImportError:
    print("📥 Pyrogram or dependencies missing! Installing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyrogram==2.0.106", "tgcrypto==1.2.5"])
    from pyrogram import Client, filters
    from pyrogram.raw import functions, types

# 🔑 image_5.png से लिए गए आपके लाइव क्रेडेंशियल्स
API_ID = 32569415
API_HASH = "4209968745cb99d37820d5ba7b4845bd"
BOT_TOKEN = "8828282788:AAGInprGjqWecQuSnZDsK7oQKY7zgEaHcd0"

app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🤖 टेलीग्राम /start कमांड हैंडलर
@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    welcome_msg = (
        "🎙️ **AUTO-UNMUTE PRO ENGINE ACTIVE** 🎙️\n\n"
        "मुझे अपने चैनल या ग्रुप में एडमिन बनाएं और 'Manage Video Chats' (या Invite Users) की परमिशन दें।\n\n"
        "⚙️ **कमांड्स:**\n"
        "🔹 `/unmuteall` - वॉइस चैट पर मौजूद सभी हैंड-रेज़ करने वालों को एक साथ अनम्यूट करें।"
    )
    await message.reply_text(welcome_msg)

# 🔥 [MAGIC NODE] जैसे ही कोई वॉइस कॉल पर हाथ उठाएगा, बॉट उसे तुरंत अनम्यूट कर देगा
@app.on_raw_update()
async def handle_voice_chat_updates(client, update, users, chats):
    if isinstance(update, types.UpdateGroupCallParticipants):
        for participant in update.participants:
            # अगर यूजर ने हाथ उठाया है (Raise Hand किया है) और वह म्यूटेड है
            if participant.raise_hand_rating and participant.muted:
                user_id = participant.peer.user_id if hasattr(participant.peer, 'user_id') else getattr(participant.peer, 'channel_id', None)
                
                if user_id:
                    try:
                        # यूजर को तुरंत बोलने की परमिशन (Unmute) देना
                        await client.invoke(
                            functions.phone.EditGroupCallParticipant(
                                call=update.call,
                                peer=await client.resolve_peer(user_id),
                                muted=False # False यानी अनम्यूट
                            )
                        )
                        print(f"✅ Automatically allowed to speak - User/Channel ID: {user_id}")
                    except Exception as e:
                        print(f"❌ Failed to auto-unmute: {e}")

# 📢 /unmuteall कमांड - एक सिंगल क्लिक में सबको परमिशन देने के लिए
@app.on_message(filters.command("unmuteall") & (filters.group | filters.channel))
async def unmute_all_participants(client, message):
    chat_id = message.chat.id
    status = await message.reply_text("🔄 *Scanning live voice chat infrastructure...*")
    
    try:
        chat_peer = await client.resolve_peer(chat_id)
        full_chat = await client.invoke(functions.channels.GetFullChannel(channel=chat_peer))
        group_call = full_chat.full_chat.call
        
        if not group_call:
            await status.edit("⚠️ इस समय इस चैनल/ग्रुप में कोई एक्टिव वॉइस चैट नहीं चल रही है।")
            return

        # कॉल के मेंबर्स की लिस्ट निकालना
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
        
        await status.edit(f"🔥 **सफलता!** वॉइस चैट पर मौजूद सभी `{unmuted_count}` म्यूटेड यूज़र्स को अनम्यूट कर दिया गया है।")
        
    except Exception as e:
        await status.edit(f"❌ **एरर:** {str(e)}\n*(सुनिश्चित करें कि बॉट वॉइस चैट का एडमिन है)*")

if __name__ == "__main__":
    print("🚀 AutoUnmute Pro Bot Engine Started Successfully...")
    app.run()
