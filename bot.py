import asyncio
import logging
import os
import urllib.request
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import init_db
from handlers import start, menu, order

# Logger sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

import ssl

def format_url(url_str):
    if not url_str:
        return ""
    url_str = url_str.strip().rstrip("/")
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        return f"https://{url_str}"
    return url_str

async def keep_alive():
    """Render'da botni uxlatmaslik uchun har 2.5 daqiqada (150s) ping yuborish"""
    raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
    url = format_url(raw_url)
    if url.endswith("/webapp"):
        url = url[:-7]

    port = os.getenv("PORT", "5000")
    ssl_ctx = ssl._create_unverified_context()

    logging.info(f"Keep-alive (Bot) ishga tushdi. Target URL: {url or 'Faqat localhost'}")

    # Dastlab 3 soniya kutib, birinchi pingni yuboramiz
    await asyncio.sleep(3)

    while True:
        # Local ping
        try:
            req_local = urllib.request.Request(f"http://127.0.0.1:{port}/ping")
            await asyncio.to_thread(urllib.request.urlopen, req_local, timeout=10)
        except Exception as e:
            logging.warning(f"Local ping xatosi: {e}")

        # External ping (Render external URL uxlamasligi uchun)
        if url:
            try:
                ping_url = f"{url}/ping"
                req_ext = urllib.request.Request(
                    ping_url,
                    headers={"User-Agent": "KeepAlive-Bot/1.0"}
                )
                await asyncio.to_thread(urllib.request.urlopen, req_ext, timeout=15, context=ssl_ctx)
                logging.info(f"Keep-alive (Bot) ping muvaffaqiyatli: {ping_url}")
            except Exception as e:
                logging.warning(f"External keep-alive (Bot) ping xatosi: {e}")

        # 150 soniya (2.5 daqiqa) kutish
        await asyncio.sleep(150)

async def main():
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token or bot_token.strip() in ("", "YOUR_BOT_TOKEN_HERE"):
        logging.error("BOT_TOKEN topilmadi! .env yoki Render Environment Variables ga kiriting.")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # Barcha botga yozgan foydalanuvchilarni avtomatik bazaga qo'shish middleware
    from database.db import add_user
    @dp.message.outer_middleware()
    async def auto_register_middleware(handler, event, data):
        try:
            u = getattr(event, 'from_user', None)
            if u and u.id and not u.is_bot:
                await add_user(u.id, "", 0.0, 0.0)
        except Exception as ex:
            logging.warning(f"auto_register_middleware error: {ex}")
        return await handler(event, data)

    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(order.router)

    # Keep-alive task ni ishga tushirish (event loop tayyor bo'lgandan keyin)
    asyncio.create_task(keep_alive())

    # Bot komandalarini va Menyuni avtomatik sozlash
    from keyboards.reply import WEB_APP_URL
    try:
        # Telegram qidiruvida "C", "Cafe", "Kafe" deb qidirganda ham birinchilardan chiqishi uchun ism va tavsiflarni indekslash
        try:
            await bot.set_my_name(name="Cafe Express 🍔 | Fast Food & Taomlar")
        except Exception as e:
            logging.warning(f"set_my_name error: {e}")

        try:
            await bot.set_my_short_description(short_description="Cafe Express — Fast Food, Pitssa, Ichimliklar va Taomlar yetkazib berish boti. Cafe, Kafe, C.")
        except Exception as e:
            logging.warning(f"set_my_short_description error: {e}")

        try:
            await bot.set_my_description(description="Welcome to Cafe Express! Mazali taomlar, pitssa, burger va ichimliklarni tezda buyurtma qiling.")
        except Exception as e:
            logging.warning(f"set_my_description error: {e}")

        await bot.set_my_commands([
            BotCommand(command="start", description="Botni qayta ishga tushirish"),
            BotCommand(command="menu", description="Menyuni ochish"),
            BotCommand(command="help", description="Yordam va qoidalar")
        ])
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="🍔 Menyu", web_app=WebAppInfo(url=WEB_APP_URL))
        )
        logging.info(f"WebApp URL: {WEB_APP_URL}")
    except Exception as e:
        logging.warning(f"Komandalar va nomlarni o'rnatishda xatolik: {e}")

    logging.info("Bot ishga tushirildi, polling boshlanmoqda...")

    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except Exception as e:
        logging.warning(f"delete_webhook error: {e}")

    # Polling - avtomatik qayta ulanish bilan
    while True:
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as e:
            logging.error(f"Polling xatosi: {e}. 10 soniyadan so'ng qayta uriniladi...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
