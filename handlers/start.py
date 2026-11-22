import os
import html
import logging
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import add_user, get_user, get_tenant_by_bot_token, get_welcome_settings
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
        'name': 'City Milliy Taomlar',
        'slug': 'express'
    }

@router.message(CommandStart())
@router.message(lambda msg: bool(msg.text and msg.text.strip().lower() in ['/start', 'start', '/boshlash', 'boshlash']))
async def cmd_start(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'City Milliy Taomlar')
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

    # Admin tomonidan kiritilgan maxsus xabar va rasm bormi?
    welcome_msg_custom, welcome_img_custom = None, None
    try:
        welcome_msg_custom, welcome_img_custom = await get_welcome_settings(tenant_id)
    except Exception as wse:
        logging.warning(f"cmd_start welcome_settings note: {wse}")

    if welcome_msg_custom and welcome_msg_custom.strip():
        custom_txt = welcome_msg_custom.strip()
        custom_txt = custom_txt.replace('{ism}', user_name).replace('{name}', user_name)
        custom_txt = custom_txt.replace('{oshxona}', html.escape(tenant_name)).replace('{cafe}', html.escape(tenant_name))
        welcome_text = custom_txt
    else:
        welcome_text = (
            f"✨ <b>{greeting_header} xush kelibsiz, {user_name}!</b>\n\n"
            f"🥘 <b>City Milliy Taomlar</b> — Eng mazali milliy va tansiq taomlarni tez fursatda yetkazib beramiz!\n\n"
            f"📋 <b>Bot Buyruqlari:</b>\n"
            f"🔹 /start — Botni qayta ishga tushirish va menyuni ochish\n"
            f"🔹 /menu — Barcha taomlar va ichimliklar menyusi\n"
            f"🔹 /help — Yordam va bog'lanish ma'lumotlari\n\n"
            f"👇 Quyidagi tugma orqali menyuni ochib buyurtma berishingiz mumkin:"
        )

    kb = get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)

    # Rasm: admin yuklagan maxsus rasm yoki faqat Cafe Express (tenant 1) uchun standart logo
    photo_target = None
    if welcome_img_custom and welcome_img_custom.strip():
        img_val = welcome_img_custom.strip()
        if img_val.startswith('http://') or img_val.startswith('https://'):
            photo_target = img_val
        else:
            clean_local = img_val.lstrip('/')
            if os.path.exists(clean_local):
                photo_target = FSInputFile(clean_local)
    elif tenant_id == 1 and os.path.exists("static/cafe_logo.png"):
        photo_target = FSInputFile("static/cafe_logo.png")

    photo_sent = False
    if photo_target:
        try:
            await message.answer_photo(
                photo=photo_target, 
                caption=welcome_text, 
                parse_mode="HTML", 
                reply_markup=kb
            )
            photo_sent = True
        except Exception as pe:
            logging.warning(f"Rasm yuborishda ogohlantirish: {pe}")

    if not photo_sent:
        try:
            await message.answer(
                welcome_text, 
                parse_mode="HTML", 
                reply_markup=kb
            )
        except Exception as me:
            logging.error(f"Xabar yuborishda xatolik: {me}")
            await message.answer(
                f"{tenant_name} botiga xush kelibsiz!\n\nMenyuni ko'rish uchun pastdagi Menyu tugmasini bosing:",
                reply_markup=kb
            )

@router.message(Command("menu"))
@router.message(lambda msg: bool(msg.text and msg.text.strip().lower() in ['/menu', 'menu', 'menyu', '🍴 menyu', '🍔 menyu']))
async def cmd_menu(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'City Milliy Taomlar')
    tenant_slug = cur_tenant.get('slug', 'express')

    await message.answer(
        f"✨ <b>{html.escape(tenant_name)} Menyusi</b>\n\nBuyurtma berish uchun quyidagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)
    )

@router.message(lambda msg: bool(msg.text and any(k in msg.text.lower() for k in ['call markazi', 'call markaz', '95 260 40 40', 'call', 'qo\'ng\'iroq', 'qongiroq'])))
async def cmd_call_center(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'City Milliy Taomlar')
    tenant_slug = cur_tenant.get('slug', 'express')

    text = (
        f"📞 <b>{html.escape(tenant_name)} — Call Markazi</b>\n\n"
        f"Savollar, buyurtmalar yoki yetkazib berish bo'yicha bog'lanish uchun:\n\n"
        f"☎️ <b>Telefon:</b> <a href=\"tel:+998952604040\">+998 95 260 40 40</a>\n"
        f"⏰ <b>Ish vaqti:</b> 09:00 dan 23:00 gacha\n\n"
        f"<i>Raqam ustiga bosib to'g'ridan-to'g'ri qo'ng'iroq qilishingiz mumkin!</i>"
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Telegram Support (@City_4040)", url="https://t.me/City_4040")]
    ])
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=inline_kb
    )

@router.message(lambda msg: bool(msg.text and any(k in msg.text.lower() for k in ['telegram suport', 'telegram support', 'suport', 'support', 'adminga yozish', 'qollab'])))
async def cmd_telegram_support(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'City Milliy Taomlar')

    text = (
        f"💬 <b>{html.escape(tenant_name)} — Telegram Qo'llab-quvvatlash</b>\n\n"
        f"Savollaringiz, takliflaringiz yoki yordam kerak bo'lsa, adminga to'g'ridan-to'g'ri yozishingiz mumkin:\n\n"
        f"👉 <b>Telegram:</b> <a href=\"https://t.me/City_4040\">@City_4040</a>\n\n"
        f"<i>Pastdagi tugmani bosing va adminga o'ting:</i>"
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Telegram Support ochish (@City_4040)", url="https://t.me/City_4040")]
    ])
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=inline_kb
    )

@router.message(Command("help"))
@router.message(lambda msg: bool(msg.text and msg.text.strip().lower() in ['/help', 'help', 'yordam', '/yordam', '📞 yordam', 'ℹ️ yordam', "bog'lanish", 'aloqa']))
async def cmd_help(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_name = cur_tenant.get('name', 'City Milliy Taomlar')
    tenant_slug = cur_tenant.get('slug', 'express')
    tenant_id = cur_tenant.get('id', 1)

    # Bog'lanish kontaktlari
    admin_contact = "+998 95 260 40 40"
    admin_id = str(cur_tenant.get('admin_telegram_id', '')).strip()

    contact_lines = [
        f"📞 Call-markaz: <b>{admin_contact}</b>",
        f"💬 Telegram Support: <a href=\"https://t.me/City_4040\">@City_4040</a>"
    ]
    if admin_id and admin_id.isdigit():
        contact_lines.append(f"👤 Admin: <a href=\"tg://user?id={admin_id}\">Admin bilan bog'lanish</a>")

    contact_block = "\n".join(contact_lines)

    help_text = (
        f"📞 <b>{html.escape(tenant_name)} — Bog'lanish va Yordam</b>\n\n"
        f"• 🍔 <b>Menyuni ko'rish:</b> Pastdagi <b>Menyu (Mini App)</b> tugmasini bosing va kerakli taomlarni tanlang.\n"
        f"• 🛵 <b>Yetkazib berish:</b> Buyurtma bergach, tasdiqlash xabari to'g'ridan-to'g'ri shu yerga keladi.\n"
        f"• 🔄 <b>Qayta ishga tushirish:</b> Agar bot to'xtab qolsa yoki menyu yangilanmasa /start buyrug'ini bosing.\n\n"
        f"{contact_block}"
    )

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Telegram Support (@City_4040)", url="https://t.me/City_4040")]
    ])

    await message.answer(
        help_text,
        parse_mode="HTML",
        reply_markup=inline_kb
    )

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """Admin ID sini bilish uchun"""
    await message.answer(
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Ushbu ID ni buyurtmalar haqida xabarnoma olish uchun .env faylidagi <b>ADMIN_ID</b> maydoniga kiritishingiz mumkin.",
        parse_mode="HTML"
    )
