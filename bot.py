import asyncio
import logging
import os
import re
import urllib.request
import ssl
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import init_db, get_all_active_tenants, add_user, get_tenant_by_id, get_all_custom_commands
from handlers import start, menu, order, custom_commands

# Logger sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

def format_url(url_str):
    if not url_str:
        return "https://telegram-bot-2-j4nb.onrender.com"
    url_str = url_str.strip().rstrip("/")
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        return f"https://{url_str}"
    return url_str

async def keep_alive():
    """Render'da botni uxlatmaslik uchun har 2 daqiqada (120s) ping yuborish"""
    raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "") or "https://telegram-bot-2-j4nb.onrender.com"
    url = format_url(raw_url)
    if url.endswith("/webapp"):
        url = url[:-7]

    port = os.getenv("PORT", "5000")
    ssl_ctx = ssl._create_unverified_context()

    logging.info(f"Keep-alive (Bot) ishga tushdi. Target URL: {url or 'Faqat localhost'}")
    await asyncio.sleep(3)

    while True:
        try:
            req_local = urllib.request.Request(f"http://127.0.0.1:{port}/ping")
            await asyncio.to_thread(urllib.request.urlopen, req_local, timeout=10)
        except Exception as e:
            logging.warning(f"Local ping xatosi: {e}")

        if url and "your-app" not in url:
            try:
                ping_url = f"{url}/ping"
                req_ext = urllib.request.Request(
                    ping_url,
                    headers={"User-Agent": "KeepAlive-Bot/2.0"}
                )
                await asyncio.to_thread(urllib.request.urlopen, req_ext, timeout=15, context=ssl_ctx)
                logging.info(f"Keep-alive (Bot) ping muvaffaqiyatli: {ping_url}")
            except Exception as e:
                logging.warning(f"External keep-alive (Bot) ping xatosi: {e}")

        await asyncio.sleep(120)

async def main():
    # 1. Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # 2. Token va Oshxona profili ma'lumotlarini aniqlash
    token = os.getenv("BOT_TOKEN", "").strip()
    tenant_info = None

    try:
        active_tenants = await get_all_active_tenants()
        if active_tenants:
            tenant_info = active_tenants[0]
            if (not token or any(ph in token.upper() for ph in ["YOUR_", "_HERE", "PLACEHOLDER"])) and tenant_info.get('bot_token'):
                db_t = tenant_info['bot_token'].strip()
                if db_t and not any(ph in db_t.upper() for ph in ["YOUR_", "_HERE", "PLACEHOLDER"]):
                    token = db_t
    except Exception as e:
        logging.warning(f"Baza tenant ma'lumotlarini olishda ogohlantirish: {e}")

    if not tenant_info:
        tenant_info = {
            'id': 1,
            'name': 'Cafe Express',
            'slug': 'express',
            'admin_telegram_id': os.getenv("ADMIN_ID", "")
        }

    # Agar token hali kiritilmagan bo'lsa
    if not token or any(ph in token.upper() for ph in ["YOUR_", "_HERE", "PLACEHOLDER"]):
        logging.error("❌ BOT_TOKEN topilmadi yoki placeholder holatida! Iltimos, .env fayliga haqiqiy BOT_TOKEN ni kiriting.")
        asyncio.create_task(keep_alive())
        while True:
            await asyncio.sleep(3600)

    bot = Bot(token=token)
    bot.tenant = tenant_info

    dp = Dispatcher(storage=MemoryStorage())

    # Avtomatik foydalanuvchini ro'yxatga olish middleware
    @dp.message.outer_middleware()
    async def auto_register_middleware(handler, event, data):
        try:
            u = getattr(event, 'from_user', None)
            if u and u.id and not u.is_bot:
                t_id = 1
                tenant_data = data.get('tenant')
                if tenant_data and isinstance(tenant_data, dict):
                    t_id = tenant_data.get('id', 1)
                await add_user(u.id, "", 0.0, 0.0, tenant_id=t_id)
        except Exception as ex:
            logging.warning(f"auto_register_middleware error: {ex}")
        return await handler(event, data)

    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(custom_commands.router)
    dp.include_router(menu.router)
    dp.include_router(order.router)

    # WebApp URL va bot komandalarini sozlash
    try:
        me = await bot.get_me()
        bot_username = me.username or "Bot"
        logging.info(f"🤖 Bot muvaffaqiyatli tanildi: @{bot_username} (ID: {me.id})")

        raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
        base_url = format_url(raw_url)
        web_app_url = f"{base_url}/webapp" if base_url else "https://your-app.onrender.com/webapp"

        base_cmds = [
            BotCommand(command="start", description="Botni qayta ishga tushirish"),
            BotCommand(command="menu", description="Menyuni ochish"),
            BotCommand(command="help", description="Yordam va qoidalar")
        ]
        try:
            custom_cmds = await get_all_custom_commands(tenant_info.get('id', 1))
            for cc in custom_cmds:
                c_name = cc['command'].strip().lstrip('/').lower()
                if c_name not in ['start', 'menu', 'help', 'myid']:
                    desc = cc.get('description', '') or c_name
                    safe_c_name = re.sub(r'[^a-z0-9_]', '_', c_name)[:32]
                    if safe_c_name:
                        base_cmds.append(BotCommand(command=safe_c_name, description=desc[:255]))
        except Exception as dbe:
            logging.warning(f"Custom commands yuklashda ogohlantirish: {dbe}")

        await bot.set_my_commands(base_cmds)
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="🍔 Menyu", web_app=WebAppInfo(url=web_app_url))
        )
        await bot.delete_webhook(drop_pending_updates=False)
        logging.info(f"✅ Bot @{bot_username} muvaffaqiyatli sozlandi. WebApp: {web_app_url}")
    except Exception as se:
        logging.warning(f"Bot komandalarini sozlashda ogohlantirish: {se}")

    # Keep-alive ni fonda ishga tushirish
    asyncio.create_task(keep_alive())

    logging.info(f"🚀 Telegram Bot (@{getattr(bot, 'username', 'Bot')}) polling rejimida ishga tushdi!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), tenant=tenant_info)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")
