import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

# 1. Avval foydalanuvchi kiritgan WEB_APP_URL ni qidiramiz
env_web_app = os.getenv("WEB_APP_URL")
# 2. Agar yo'q bo'lsa, Render bergan URL ni qidiramiz
render_url = os.getenv("RENDER_EXTERNAL_URL")

if env_web_app:
    WEB_APP_URL = env_web_app
elif render_url:
    WEB_APP_URL = f"{render_url.rstrip('/')}/webapp"
else:
    WEB_APP_URL = "https://quickly-sessions-creamer.ngrok-free.dev/webapp"

def get_webapp_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍔 Menyu (Mini App)", web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True
    )

def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
