import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db

LOG_TEXT = """<b>#NewUser

ID - <code>{}</code>
Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command("start"))
async def start_message(c, m):
    if m.from_user is None:
        return  # Skip messages from anonymous admins or channels

    user_id = m.from_user.id
    name = m.from_user.first_name

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, name)
        await c.send_message(
            LOG_CHANNEL, LOG_TEXT.format(user_id, m.from_user.mention)
        )

    await m.reply_photo(
        photo="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=(
            f"<b>Hello {m.from_user.mention} 👋\n\n"
            "I am a Join Request Acceptor Bot. I can accept all old pending join requests.\n\n"
            "To approve all pending requests, use: /accept</b>"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💝 JOIN BOT SUPPORT GROUP", url="https://t.me/colonel_support")],
            [
                InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/sayeedmasoo"),
                InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url="https://t.me/colonol_updates")
            ]
        ])
    )

@Client.on_message(filters.command("accept") & filters.private)
async def accept(client, message):
    user_id = message.from_user.id
    show = await message.reply("**Please wait...**")

    user_data = await db.get_session(user_id)
    if user_data is None:
        await show.edit("**You need to /login first before accepting join requests.**")
        return

    try:
        acc = Client(
            "joinrequest", session_string=user_data,
            api_hash=API_HASH, api_id=API_ID
        )
        await acc.connect()
    except Exception:
        await show.edit("**Your session expired. Please /logout and then /login again.**")
        return

    await show.edit("**Forward a message from your channel/group to begin (must include forward tag).**")
    try:
        vj = await client.listen(message.chat.id)
    except Exception as e:
        return await message.reply(f"**Error waiting for forward: {e}**")

    if not vj.forward_from_chat or vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        return await message.reply("**Message not forwarded from a valid group or channel.**")

    chat_id = vj.forward_from_chat.id
    await vj.delete()

    try:
        await acc.get_chat(chat_id)
    except Exception:
        return await show.edit("**Bot is not admin in the forwarded group/channel.**")

    msg = await show.edit("**Accepting all join requests... Please wait.**")

    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            requests = [req async for req in acc.get_chat_join_requests(chat_id)]
            if not requests:
                break
        await msg.edit("✅ Successfully accepted all join requests.")
    except Exception as e:
        await msg.edit(f"❌ An error occurred: `{str(e)}`")

@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE or m.from_user is None:
        return

    user_id = m.from_user.id
    try:
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, m.from_user.first_name)
            await client.send_message(
                LOG_CHANNEL, LOG_TEXT.format(user_id, m.from_user.mention)
            )

        await client.approve_chat_join_request(m.chat.id, user_id)

        try:
            await client.send_message(
                user_id,
                f"**Hello {m.from_user.mention}!\nWelcome to {m.chat.title}**\n\n__Powered By : @said__"
            )
        except:
            pass  # user might have PMs closed
    except Exception as e:
        print(f"Join request error: {e}")


