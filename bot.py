import asyncio
import logging
import os
import urllib.request
import ssl
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import init_db, get_all_active_tenants, add_user, get_tenant_by_bot_token
from handlers import start, menu, order

# Logger sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

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
    await asyncio.sleep(3)

    while True:
        try:
            req_local = urllib.request.Request(f"http://127.0.0.1:{port}/ping")
            await asyncio.to_thread(urllib.request.urlopen, req_local, timeout=10)
        except Exception as e:
            logging.warning(f"Local ping xatosi: {e}")

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

        await asyncio.sleep(150)

# Multi-Bot dinamik boshqaruvi
running_bots = {}  # {tenant_id: {'bot': bot, 'token': token, 'task': task, 'username': username}}

async def start_single_bot(tenant, dp: Dispatcher):
    token = tenant.get('bot_token', '').strip()
    if not token or token in ("YOUR_BOT_TOKEN_HERE", ""):
        return

    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        bot_username = me.username or "Bot"

        raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
        base_url = format_url(raw_url)
        slug = tenant.get('slug', 'express')
        web_app_url = f"{base_url}/webapp?tenant={slug}" if base_url else f"https://your-app.onrender.com/webapp?tenant={slug}"

        # Komandalar va WebApp tugmasini sozlash
        try:
            await bot.set_my_commands([
                BotCommand(command="start", description="Botni qayta ishga tushirish"),
                BotCommand(command="menu", description="Menyuni ochish"),
                BotCommand(command="help", description="Yordam va qoidalar")
            ])
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="🍔 Menyu", web_app=WebAppInfo(url=web_app_url))
            )
            await bot.delete_webhook(drop_pending_updates=False)
            logging.info(f"Bot @{bot_username} sozlandi. WebApp: {web_app_url}")
        except Exception as ce:
            logging.warning(f"Komandalarni sozlashda xatolik (@{bot_username}): {ce}")

        # Polling vazifasini alohida taskda boshlash
        async def run_bot_polling(b: Bot, username: str):
            while True:
                try:
                    logging.info(f"Polling boshlandi: @{username} (Oshxona: {tenant.get('name')})")
                    await dp.start_polling(b, allowed_updates=dp.resolve_used_update_types())
                except asyncio.CancelledError:
                    logging.info(f"Polling to'xtatildi: @{username}")
                    break
                except Exception as pe:
                    logging.error(f"Polling xatosi (@{username}): {pe}. 10 soniyadan so'ng qayta ulanadi...")
                    await asyncio.sleep(10)

        task = asyncio.create_task(run_bot_polling(bot, bot_username))
        running_bots[tenant['id']] = {
            'bot': bot,
            'token': token,
            'task': task,
            'username': bot_username
        }
    except Exception as e:
        logging.error(f"Botni ishga tushirishda xatolik ({tenant.get('name')}): {e}")

async def dynamic_bot_watcher(dp: Dispatcher):
    """Bazada yangi qo'shilgan, tahrirlangan yoki to'xtatilgan oshxonalarni kuzatib boradi"""
    while True:
        try:
            active_tenants = await get_all_active_tenants()
            active_ids = {t['id'] for t in active_tenants}

            # 1. Yangi yoki o'zgargan tokenli botlarni ishga tushirish
            for t in active_tenants:
                tid = t['id']
                if tid not in running_bots:
                    await start_single_bot(t, dp)
                elif running_bots[tid]['token'] != t.get('bot_token', ''):
                    logging.info(f"Bot tokeni yangilandi (ID {tid}). Qayta ishga tushirilmoqda...")
                    running_bots[tid]['task'].cancel()
                    await start_single_bot(t, dp)

            # 2. Bloklangan yoki o'chirilgan botlarni to'xtatish
            stopped_ids = [tid for tid in list(running_bots.keys()) if tid not in active_ids]
            for tid in stopped_ids:
                logging.info(f"Bot to'xtatilmoqda: Tenant ID {tid}")
                running_bots[tid]['task'].cancel()
                del running_bots[tid]

        except Exception as ex:
            logging.error(f"dynamic_bot_watcher error: {ex}")

        await asyncio.sleep(10)

async def main():
    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    dp = Dispatcher(storage=MemoryStorage())

    # Avtomatik foydalanuvchini bazaga qo'shish middleware
    @dp.message.outer_middleware()
    async def auto_register_middleware(handler, event, data):
        try:
            u = getattr(event, 'from_user', None)
            bot_obj = data.get('bot')
            if u and u.id and not u.is_bot and bot_obj:
                tenant = await get_tenant_by_bot_token(bot_obj.token)
                t_id = tenant['id'] if tenant else 1
                await add_user(u.id, "", 0.0, 0.0, tenant_id=t_id)
        except Exception as ex:
            logging.warning(f"auto_register_middleware error: {ex}")
        return await handler(event, data)

    # Routerni ulash
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(order.router)

    # Keep-alive va Bot Watcher ni ishga tushirish
    asyncio.create_task(keep_alive())
    asyncio.create_task(dynamic_bot_watcher(dp))

    logging.info("Multi-Bot Dynamic Manager ishga tushdi!")

    # Event loopni ushlab turish
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Botlar to'xtatildi!")
