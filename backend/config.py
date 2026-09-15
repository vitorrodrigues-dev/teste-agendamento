import os

from dotenv import load_dotenv

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")

NAGER_API_BASE = os.getenv("NAGER_API_BASE", "https://date.nager.at/api/v3")

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
