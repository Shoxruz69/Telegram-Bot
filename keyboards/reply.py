import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

# WEB_APP_URL ni aniqlash (muhit o'zgaruvchilari orqali)
env_web_app = os.getenv("WEB_APP_URL")       # Agar maxsus URL bergan bo'lsangiz
render_url = os.getenv("RENDER_EXTERNAL_URL")  # Render avtomatik beradi

if env_web_app:
    WEB_APP_URL = env_web_app
elif render_url:
    WEB_APP_URL = f"{render_url.rstrip('/')}/webapp"
else:
    # Render URL topilmasa bo'sh - bot ishga tushmaydi, lekir xato chiqaradi
    WEB_APP_URL = "https://your-app.onrender.com/webapp"
    import logging
    logging.warning("DIQQAT: WEB_APP_URL yoki RENDER_EXTERNAL_URL topilmadi! Render Environment Variables ni tekshiring.")

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
