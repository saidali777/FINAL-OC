from os import environ

API_ID = int(environ.get("API_ID", "12618934"))
API_HASH = environ.get("API_HASH", "49aacd0bc2f8924add29fb02e20c8a16")
BOT_TOKEN = environ.get("BOT_TOKEN", "7934428209:AAF4VkZbSNnfK_JD1lHGXoEPu9zAo7kISB0")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002608373784"))
ADMINS = int(environ.get("ADMINS", "7837304801"))

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "vjjoinrequetbot")

# If this is True Then Bot Accept New Join Request 
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
