import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

# WEB_APP_URL ni aniqlash (muhit o'zgaruvchilari orqali)
env_web_app = os.getenv("WEB_APP_URL")       # Agar maxsus URL bergan bo'lsangiz
render_url = os.getenv("RENDER_EXTERNAL_URL")  # Render avtomatik beradi

def format_url(url_str):
    if not url_str:
        return ""
    url_str = url_str.strip().rstrip("/")
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        return f"https://{url_str}"
    return url_str

raw_base = format_url(env_web_app or render_url or "https://telegram-bot-2-j4nb.onrender.com")
if not raw_base or "your-app" in raw_base:
    raw_base = "https://telegram-bot-2-j4nb.onrender.com"

WEB_APP_URL = raw_base if raw_base.endswith("/webapp") else f"{raw_base}/webapp"

def get_webapp_keyboard(user_id: int = None, tenant_slug: str = None):
    slug = tenant_slug or "express"
    params = [f"tenant={slug}"]
    if user_id:
        params.append(f"user_id={user_id}")
    
    query = f"?{'&'.join(params)}"
    url = f"{WEB_APP_URL}{query}"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍔 Menyu (Mini App)", web_app=WebAppInfo(url=url))]
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
