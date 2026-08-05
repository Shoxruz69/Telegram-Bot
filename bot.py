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

async def keep_alive():
    """Render'da botni uxlatmaslik uchun har 10 daqiqada ping yuborish"""
    url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    if not url:
        logging.info("RENDER_EXTERNAL_URL topilmadi. Keep-alive o'chirilgan.")
        return

    logging.info(f"Keep-alive ishga tushdi: {url}/ping")
    while True:
        await asyncio.sleep(600)  # 10 daqiqa kutish
        try:
            await asyncio.to_thread(urllib.request.urlopen, f"{url}/ping", timeout=10)
            logging.info(f"Keep-alive ping yuborildi: {url}/ping")
        except Exception as e:
            logging.warning(f"Keep-alive ping xatosi: {e}")

async def main():
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token or bot_token.strip() in ("", "YOUR_BOT_TOKEN_HERE"):
        logging.error("BOT_TOKEN topilmadi! .env yoki Render Environment Variables ga kiriting.")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(order.router)

    # Keep-alive task ni ishga tushirish (event loop tayyor bo'lgandan keyin)
    asyncio.create_task(keep_alive())

    # Bot komandalarini va Menyuni avtomatik sozlash
    from keyboards.reply import WEB_APP_URL
    try:
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
        logging.warning(f"Komandalar o'rnatishda xatolik: {e}")

    logging.info("Bot ishga tushirildi, polling boshlanmoqda...")

    # Polling - avtomatik qayta ulanish bilan
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as e:
            logging.error(f"Polling xatosi: {e}. 15 soniyadan so'ng qayta uriniladi...")
            await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
