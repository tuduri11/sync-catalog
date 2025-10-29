import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://catalog:catalog@postgres:5432/catalog",
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")

AUTO_RUN = os.getenv("AUTO_RUN", "true").lower() == "true"

FEED_PATH = os.getenv("FEED_PATH", "data/feed_items.csv")
PORTAL_PATH = os.getenv("PORTAL_PATH", "data/portal_items.csv")