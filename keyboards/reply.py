import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

render_url = os.getenv("RENDER_EXTERNAL_URL")
if render_url:
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
