import os
import re
import html
import logging
from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from database.db import get_custom_command
from keyboards.reply import get_webapp_keyboard
from handlers.start import resolve_tenant

router = Router()

@router.message(F.text.startswith("/"))
async def handle_custom_command(message: Message, bot: Bot, tenant: dict = None):
    """Admin tomonidan qo'shilgan ixtiyoriy /komandalarni qayta ishlash"""
    if not message.text:
        return

    text = message.text.strip()
    parts = text.split()
    if not parts:
        return

    # /manzil yoki /manzil@BotUsername dan faqat komanda nomini olish
    raw_cmd = parts[0].split('@')[0].lstrip('/').lower()
    clean_cmd = re.sub(r'[^a-z0-9_]', '', raw_cmd)

    # Standart bot komandalarini start/menu routerlariga qoldirish
    if clean_cmd in ['start', 'menu', 'help', 'myid', 'boshlash', 'yordam']:
        return

    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    tenant_name = cur_tenant.get('name', 'Cafe Express')
    tenant_slug = cur_tenant.get('slug', 'express')

    cmd_data = await get_custom_command(tenant_id, clean_cmd)
    if not cmd_data:
        return

    user_name = "Mijoz"
    if message.from_user and message.from_user.full_name:
        user_name = html.escape(message.from_user.full_name)

    reply_text = cmd_data.get('reply_text', '') or ''
    reply_text = reply_text.replace('{ism}', user_name).replace('{name}', user_name)
    reply_text = reply_text.replace('{oshxona}', html.escape(tenant_name)).replace('{cafe}', html.escape(tenant_name))

    kb = get_webapp_keyboard(message.from_user.id, tenant_slug=tenant_slug)

    # Rasm yuborish
    reply_image = cmd_data.get('reply_image', '')
    photo_target = None
    if reply_image and reply_image.strip():
        img_val = reply_image.strip()
        if img_val.startswith('http://') or img_val.startswith('https://'):
            photo_target = img_val
        else:
            clean_local = img_val.lstrip('/')
            if os.path.exists(clean_local):
                photo_target = FSInputFile(clean_local)

    if photo_target:
        try:
            await message.answer_photo(
                photo=photo_target,
                caption=reply_text,
                parse_mode="HTML",
                reply_markup=kb
            )
            return
        except Exception as pe:
            logging.warning(f"Custom command ({clean_cmd}) photo send error: {pe}")

    try:
        await message.answer(
            reply_text,
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as me:
        logging.error(f"Custom command ({clean_cmd}) send error: {me}")
        await message.answer(reply_text, reply_markup=kb)
