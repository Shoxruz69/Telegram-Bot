import os
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from database.db import add_user, get_user, get_tenant_by_bot_token
from keyboards.reply import get_webapp_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    tenant = await get_tenant_by_bot_token(bot.token)
    tenant_name = tenant['name'] if tenant else "Cafe Express"
    tenant_slug = tenant['slug'] if tenant else "express"
    tenant_id = tenant['id'] if tenant else 1

    # Foydalanuvchini ro'yxatga olish
    user = await get_user(message.from_user.id, tenant_id=tenant_id)
    if not user:
        await add_user(message.from_user.id, "", 0.0, 0.0, tenant_id=tenant_id)

    welcome_text = (
        f"☕ *{tenant_name} Botiga Xush Kelibsiz, {message.from_user.full_name}!*\n\n"
        f"🚀 *Fast & Fresh Delivery* — Mazali taomlar, pissa, burger va ichimliklarni tez fursatda yetkazib beramiz!\n\n"
        f"📋 *Bot Buyruqlari:*\n"
        f"🔹 /start — Botni qayta ishga tushirish va menyuni ochish\n"
        f"🔹 /menu — Barcha taomlar va ichimliklar menyusi\n"
        f"🔹 /help — Yordam va bog'lanish ma'lumotlari\n\n"
        f"👇 Quyidagi tugma orqali menyuni ochib buyurtma berishingiz mumkin:"
    )

    kb = get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)

    try:
        photo = FSInputFile("static/cafe_logo.png")
        await message.answer_photo(
            photo=photo, 
            caption=welcome_text, 
            parse_mode="Markdown", 
            reply_markup=kb
        )
    except Exception:
        await message.answer(
            welcome_text, 
            parse_mode="Markdown", 
            reply_markup=kb
        )

@router.message(Command("menu"))
async def cmd_menu(message: Message, bot: Bot):
    tenant = await get_tenant_by_bot_token(bot.token)
    tenant_name = tenant['name'] if tenant else "Cafe Express"
    tenant_slug = tenant['slug'] if tenant else "express"

    await message.answer(
        f"✨ *{tenant_name} Menyu*\n\nBuyurtma berish uchun quyidagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)
    )

@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    tenant = await get_tenant_by_bot_token(bot.token)
    tenant_name = tenant['name'] if tenant else "Cafe Express"
    admin_phone = "+998 88 732 55 15"

    await message.answer(
        f"📞 *{tenant_name} — Bog'lanish va Yordam*\n\n"
        f"• Barcha taomlarni ko'rish va xarid qilish uchun pastdagi 🍔 *Menyu* tugmasidan foydalaning.\n"
        f"• Buyurtma bergach, xabarnoma telegram chatingizga darhol yetib boradi.\n"
        f"• Agar xatolik kuzatilsa /start tugmasini bosing.\n\n"
        f"📞 Bog'lanish raqami: {admin_phone}",
        parse_mode="Markdown"
    )

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """Admin ID sini bilish uchun"""
    await message.answer(
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Ushbu ID ni Super Admin panelida yangi oshxona qo'shganda <b>Admin Telegram ID</b> maydoniga kiritishingiz mumkin.",
        parse_mode="HTML"
    )
