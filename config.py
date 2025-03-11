import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///support.db")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", 8443))
WEBHOOK_LISTEN = os.environ.get("WEBHOOK_LISTEN", "0.0.0.0")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
