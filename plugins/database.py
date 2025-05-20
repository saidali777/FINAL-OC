import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return {
            "id": int(id),
            "name": name,
            "session": None,
        }

    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            try:
                user = self.new_user(id, name)
                await self.col.insert_one(user)
            except Exception as e:
                print(f"Failed to add user: {e}")

    async def is_user_exist(self, id):
        try:
            user = await self.col.find_one({"id": int(id)})
            return bool(user)
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

    async def total_users_count(self):
        try:
            return await self.col.count_documents({})
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0

    async def get_all_users(self):
        try:
            return self.col.find({})
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({"id": int(user_id)})
        except Exception as e:
            print(f"Failed to delete user: {e}")

    async def set_session(self, id, session):
        try:
            await self.col.update_one(
                {"id": int(id)},
                {"$set": {"session": session}},
                upsert=True
            )
        except Exception as e:
            print(f"Failed to set session: {e}")

    async def get_session(self, id):
        try:
            user = await self.col.find_one({"id": int(id)})
            return user.get("session") if user else None
        except Exception as e:
            print(f"Failed to get session: {e}")
            return None

# Singleton DB object
db = Database(DB_URI, DB_NAME)
