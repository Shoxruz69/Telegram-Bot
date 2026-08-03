import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import init_db
from handlers import start, menu, order

# Logger sozlamalari
logging.basicConfig(level=logging.INFO)

async def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        logging.error("Iltimos .env faylida BOT_TOKEN ni kiriting!")
        return
        
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()
    
    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(order.router)
    
    logging.info("Bot ishga tushirildi...")
    
    while True:
        try:
            # Eski update larni o'tkazib yuborish va botni ishga tushirish
            await bot.delete_webhook(drop_pending_updates=True)
            
            # Bot komandalarini va Menyuni avtomatik sozlash
            from keyboards.reply import WEB_APP_URL
            await bot.set_my_commands([
                BotCommand(command="start", description="Botni qayta ishga tushirish"),
                BotCommand(command="menu", description="Menyuni ochish"),
                BotCommand(command="help", description="Yordam va qoidalar")
            ])
            await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="🍔 Menyu", web_app=WebAppInfo(url=WEB_APP_URL)))
            
            await dp.start_polling(bot)
            break
        except Exception as e:
            logging.error(f"Tarmoq xatosi: {e}. 10 soniyadan so'ng qayta uriniladi...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
