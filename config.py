from os import environ

API_ID = int(environ.get("API_ID", "26444821"))
API_HASH = environ.get("API_HASH", "a58efd1d6483e3f0d5b2757d9f665c24")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# Make Bot Admin In Log Channel With Full Rights
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002543077774"))
ADMINS = int(environ.get("ADMINS", "5473802801"))

# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = environ.get("DB_NAME", "vjjoinrequetbot")

# If this is True Then Bot Accept New Join Request 
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', True))
