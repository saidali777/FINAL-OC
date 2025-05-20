import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

# /start command handler
@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if m.from_user is None:
        return  # User info not available, do nothing

    # Add user to DB if not already there
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))

    # Send welcome message with photo
    await m.reply_photo(
        "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Request.\n\nFor All Pending Join Request Use - /accept</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('💝JOIN BOT SUPPORT GROUP', url='https://t.me/colonel_support')],
            [
                InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/sayeedmasoo'),
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/colonol_updates')
            ]
        ])
    )

# /accept command handler
@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")

    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepting Pending Requests, You Need To /login First.**")
        return

    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. Use /logout, Then /login Again.**")

    await show.edit(
        "**Now Forward A Message From Your Channel Or Group.\n\nMake Sure The Logged-In Account Is Admin There With Full Rights.**"
    )

    vj = await client.listen(message.chat.id)

    if vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            await acc.get

