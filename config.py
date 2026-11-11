import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("SL_DATA_DIR", BASE_DIR / "data"))

MONGO_HOST = os.getenv("SL_MONGO_HOST", "127.0.0.1")
MONGO_PORT = int(os.getenv("SL_MONGO_PORT", "27017"))
MONGO_DB = os.getenv("SL_MONGO_DB", "smartlibrary")
MONGO_USER = os.getenv("SL_MONGO_USER", "sl_rw")
MONGO_PASSWORD = os.getenv("SL_MONGO_PASSWORD", "ReadWrite@2026")
MONGO_AUTH = os.getenv("SL_MONGO_AUTH", "1") == "1"
