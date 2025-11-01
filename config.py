import os
from pathlib import Path

APP_NAME = "PharmaBiz Pro"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EXPIRY_WARNING_DAYS = 90
CURRENCY_SYMBOL = "₹"
