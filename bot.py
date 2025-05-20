from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="join_request_bot",  # keep it lowercase with underscores
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=16,
            sleep_threshold=10
        )

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            self.username = f"@{me.username}" if me else "UnknownBot"
            print(f"✅ Bot started as {self.username}")
        except Exception as e:
            print(f"❌ Bot failed to start: {e}")

    async def stop(self, *args):
        await super().stop()
        print("⛔ Bot stopped. Goodbye!")

# Run the bot
if __name__ == "__main__":
    Bot().run()

