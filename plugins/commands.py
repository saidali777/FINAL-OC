import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db

LOG_TEXT = """<b>#NewUser

ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if not m.from_user:
        return

    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))

    await m.reply_photo(
        "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Requests.\n\nTo Accept All Pending Join Requests, Use - /accept</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('💝JOIN BOT SUPPORT GROUP', url='https://t.me/colonel_support')],
            [
                InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/sayeedmasoo'),
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/colonol_updates')
            ]
        ])
    )


@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    if not message.from_user:
        return

    show = await message.reply("**Please wait...**")
    user_data = await db.get_session(message.from_user.id)

    if user_data is None:
        await show.edit("**To accept pending requests, please /login first.**")
        return

    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)
        await acc.connect()
    except Exception:
        return await show.edit("❌ **Login session expired. Use /logout and /login again.**")

    await show.edit(
        "**Now, forward a message from your group or channel.**\n"
        "__Make sure your logged-in account is an admin with full rights.__"
    )

    try:
        vj = await client.listen(message.chat.id)
    except asyncio.TimeoutError:
        return await show.edit("❌ **Timeout. Please try forwarding again.**")

    if not vj.forward_from_chat or vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        return await message.reply("❌ **Forwarded message must be from a group or channel.**")

    chat_id = vj.forward_from_chat.id
    try:
        await acc.get_chat(chat_id)
    except Exception:
        return await show.edit("❌ **Unable to access chat. Make sure you're an admin.**")

    await vj.delete()

    msg = await show.edit("⏳ **Accepting join requests... Please wait.**")
    attempts = 0

    try:
        while attempts < 30:  # Limit to avoid infinite loop
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [req async for req in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
            attempts += 1
        await msg.edit("✅ **All join requests have been accepted.**")
    except Exception as e:
        await msg.edit(f"❌ **Error:** `{str(e)}`")


@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return

    if not m.from_user:
        return

    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))

        await client.approve_chat_join_request(m.chat.id, m.from_user.id)

        try:
            await client.send_message(
                m.from_user.id,
                f"**Hello {m.from_user.mention}!\nWelcome to {m.chat.title}**\n\n__Powered By: @said__"
            )
        except:
            pass

    except Exception as e:
        print(f"Join approve error: {e}")

