import os
import html
import logging
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from database.db import add_user, get_user, get_tenant_by_bot_token
from keyboards.reply import get_webapp_keyboard

router = Router()

async def resolve_tenant(bot: Bot, tenant: dict = None) -> dict:
    """Oshxona ma'lumotlarini aniqlash (argument, bot obyekti yoki DB orqali)"""
    if tenant and isinstance(tenant, dict) and tenant.get('name'):
        return tenant
    
    bot_tenant = getattr(bot, 'tenant', None)
    if bot_tenant and isinstance(bot_tenant, dict) and bot_tenant.get('name'):
        return bot_tenant
        
    try:
        db_tenant = await get_tenant_by_bot_token(bot.token)
        if db_tenant:
            return db_tenant
    except Exception as ex:
        logging.warning(f"resolve_tenant DB lookup error: {ex}")

    return {
        'id': 1,
        'name': 'Cafe Express',
        'slug': 'express'
    }

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'Cafe Express')
    tenant_slug = cur_tenant.get('slug', 'express')
    tenant_id = cur_tenant.get('id', 1)

    # Foydalanuvchini ro'yxatga olish (xavfsiz rejim)
    try:
        user = await get_user(message.from_user.id, tenant_id=tenant_id)
        if not user:
            await add_user(message.from_user.id, "", 0.0, 0.0, tenant_id=tenant_id)
    except Exception as ue:
        logging.warning(f"cmd_start user registration note: {ue}")

    # Foydalanuvchi ismi
    user_name = "Mijoz"
    if message.from_user and message.from_user.full_name:
        user_name = html.escape(message.from_user.full_name)

    # Dinamik tabrik sarlavhasi (Dili Cafe -> Dili Cafe botiga; Dili bot -> Dili botga)
    name_clean = tenant_name.strip()
    if name_clean.lower().endswith("bot"):
        greeting_header = f"{html.escape(name_clean)}ga"
    else:
        greeting_header = f"{html.escape(name_clean)} botiga"

    welcome_text = (
        f"☕ <b>{greeting_header} xush kelibsiz, {user_name}!</b>\n\n"
        f"🚀 <b>Fast & Fresh Delivery</b> — Mazali taomlar, pissa, burger va ichimliklarni tez fursatda yetkazib beramiz!\n\n"
        f"📋 <b>Bot Buyruqlari:</b>\n"
        f"🔹 /start — Botni qayta ishga tushirish va menyuni ochish\n"
        f"🔹 /menu — Barcha taomlar va ichimliklar menyusi\n"
        f"🔹 /help — Yordam va bog'lanish ma'lumotlari\n\n"
        f"👇 Quyidagi tugma orqali menyuni ochib buyurtma berishingiz mumkin:"
    )

    kb = get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)

    # Avval logotip bilan yuborishga urinib ko'ramiz
    photo_sent = False
    logo_path = "static/cafe_logo.png"
    if os.path.exists(logo_path):
        try:
            photo = FSInputFile(logo_path)
            await message.answer_photo(
                photo=photo, 
                caption=welcome_text, 
                parse_mode="HTML", 
                reply_markup=kb
            )
            photo_sent = True
        except Exception as pe:
            logging.warning(f"Logo yuborishda ogohlantirish: {pe}")

    if not photo_sent:
        try:
            await message.answer(
                welcome_text, 
                parse_mode="HTML", 
                reply_markup=kb
            )
        except Exception as me:
            logging.error(f"Xabar yuborishda xatolik: {me}")
            # Eng sodda fallback (parse_mode siz)
            await message.answer(
                f"{tenant_name} botiga xush kelibsiz!\n\nMenyuni ko'rish uchun pastdagi Menyu tugmasini bosing:",
                reply_markup=kb
            )

@router.message(Command("menu"))
async def cmd_menu(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'Cafe Express')
    tenant_slug = cur_tenant.get('slug', 'express')

    await message.answer(
        f"✨ <b>{html.escape(tenant_name)} Menyusi</b>\n\nBuyurtma berish uchun quyidagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)
    )

@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'Cafe Express')
    admin_phone = "+998 88 732 55 15"

    await message.answer(
        f"📞 <b>{html.escape(tenant_name)} — Bog'lanish va Yordam</b>\n\n"
        f"• Barcha taomlarni ko'rish va xarid qilish uchun pastdagi 🍔 <b>Menyu</b> tugmasidan foydalaning.\n"
        f"• Buyurtma bergach, xabarnoma telegram chatingizga darhol yetib boradi.\n"
        f"• Agar xatolik kuzatilsa /start tugmasini bosing.\n\n"
        f"📞 Bog'lanish raqami: {admin_phone}",
        parse_mode="HTML"
    )

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """Admin ID sini bilish uchun"""
    await message.answer(
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Ushbu ID ni Super Admin panelida yangi oshxona qo'shganda <b>Admin Telegram ID</b> maydoniga kiritishingiz mumkin.",
        parse_mode="HTML"
    )
