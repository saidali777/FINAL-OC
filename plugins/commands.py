import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, SessionPasswordNeeded

from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db

LOG_TEXT = """<b>#NewUser

ID - <code>{}</code>
Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c, m):
    if m.from_user is None:
        return  # ignore if from_user is missing

    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))

        await m.reply_photo(
            "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
            caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Requests.\n\nFor All Pending Join Requests Use - /accept</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('💝JOIN BOT SUPPORT GROUP', url='https://t.me/colonel_support')],
                [
                    InlineKeyboardButton("❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ", url='https://t.me/sayeedmasoo'),
                    InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ", url='https://t.me/colonol_updates')
                ]
            ])
        )
    except Exception as e:
        print(f"Error in /start: {e}")


@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please wait...**")

    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**You must /login first to accept join requests.**")
        return

    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)

        try:
            await acc.connect()
        except FloodWait as e:
            await show.edit(f"⚠️ Rate limit hit. Sleeping for `{e.value}` seconds...")
            await asyncio.sleep(e.value)
            await acc.connect()
        except Exception as e:
            await show.edit(f"❌ Login failed: `{str(e)}`")
            return

        await show.edit("**Now forward a message from your Channel/Group (with Forward Tag).\n\nMake sure your logged-in account is Admin with full rights.**")

        vj = await client.listen(message.chat.id)
        if vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
            chat_id = vj.forward_from_chat.id
            try:
                info = await acc.get_chat(chat_id)
            except Exception:
                return await show.edit("❌ Error: Make sure your logged-in account is admin in the group/channel.")

        else:
            return await message.reply("❌ Please forward a message from a group/channel.")

        await vj.delete()

        msg = await show.edit("✅ Accepting all join requests... Please wait.")

        try:
            while True:
                try:
                    await acc.approve_all_chat_join_requests(chat_id)
                except FloodWait as e:
                    await msg.edit(f"⏱️ FloodWait: Waiting for {e.value} seconds...")
                    await asyncio.sleep(e.value)
                    continue

                await asyncio.sleep(1)
                join_requests = [r async for r in acc.get_chat_join_requests(chat_id)]
                if not join_requests:
                    break

            await msg.edit("🎉 All join requests accepted successfully!")

        except Exception as e:
            await msg.edit(f"❌ An error occurred: `{str(e)}`")

        await acc.disconnect()

    except Exception as e:
        await show.edit(f"❌ Unexpected error: `{str(e)}`")


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
                f"**Hello {m.from_user.mention}!\nWelcome to {m.chat.title} 🎉\n\n__Powered By: @said__**"
            )
        except:
            pass  # if user has PM off, silently ignore

    except Exception as e:
        print(f"Auto-approval error: {e}")




