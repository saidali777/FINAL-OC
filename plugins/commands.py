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
            await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Make Sure You're Admin In The Channel/Group With Rights.**")
            return
    else:
        return await message.reply("**Message Was Not Forwarded From A Channel Or Group.**")

    await vj.delete()

    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** `{str(e)}`")

# Auto-approve new join requests if NEW_REQ_MODE is enabled
@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return

    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))

        await client.approve_chat_join_request(m.chat.id, m.from_user.id)

        try:
            await client.send_message(
                m.from_user.id,
                f"**Hello {m.from_user.mention}!\nWelcome To {m.chat.title}\n\n__Powered By : @said__**"
            )
        except:
            pass
    except Exception as e:
        print(str(e))
        pass


