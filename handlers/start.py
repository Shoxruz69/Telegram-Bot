import json
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from database.db import add_user, get_user, clear_cart, add_to_cart, get_setting_card_number
from keyboards.reply import get_webapp_keyboard, get_contact_keyboard, get_location_keyboard
from handlers.order import finalize_order
from states import CheckoutState
import os

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Dastlabki ro'yxatdan o'tkazish
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id, "", 0.0, 0.0)
    
    welcome_text = (
        f"☕ *Cafe Express Botiga Xush Kelibsiz, {message.from_user.full_name}!*\n\n"
        f"🚀 *Fast & Fresh Delivery* — Bizning professional jamoamiz eng mazali taomlar, issiq kofe va salqin ichimliklarni tez fursatda yetkazib beradi!\n\n"
        f"📋 *Bot Buyruqlari (Komandalar bo'limi):*\n"
        f"🔹 /start — Botni qayta ishga tushirish va menyuni ochish\n"
        f"🔹 /menu — Barcha taomlar va ichimliklar menyusi\n"
        f"🔹 /help — Yordam va bog'lanish ma'lumotlari\n\n"
        f"👨‍🍳 *Jamoamiz va Xizmatimiz:* Biz mijozlarimizga har doim har xil, issiq va yuqori sifatli taomlarni taqdim etamiz!\n\n"
        f"👇 Quyidagi tugma orqali menyuni ochib buyurtma berishingiz mumkin:"
    )

    try:
        photo = FSInputFile("static/cafe_logo.png")
        await message.answer_photo(
            photo=photo, 
            caption=welcome_text, 
            parse_mode="Markdown", 
            reply_markup=get_webapp_keyboard(message.from_user.id)
        )
    except Exception:
        await message.answer(
            welcome_text, 
            parse_mode="Markdown", 
            reply_markup=get_webapp_keyboard(message.from_user.id)
        )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "✨ *Cafe Express Menyu*\n\nBuyurtma berish uchun quyidagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=get_webapp_keyboard(message.from_user.id)
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📞 *Cafe Express — Bog'lanish va Yordam*\n\n"
        "• Barcha taomlarni ko'rish va xarid qilish uchun pastdagi 🍔 *Menyu* tugmasidan foydalaning.\n"
        "• Buyurtma bergach, xabarnoma telegram chatingizga darhol yetib boradi.\n"
        "• Agar xatolik kuzatilsa /start tugmasini bosing.\n\n"
        "📞 Bog'lanish raqami: +998 88 732 55 15",
        parse_mode="Markdown"
    )

@router.message(Command("myid"))
async def cmd_myid(message: Message):
    """Admin ID sini bilish uchun"""
    admin_id = os.getenv("ADMIN_ID", "sozlanmagan")
    await message.answer(
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n\n"
        f"Hozirgi ADMIN_ID: <code>{admin_id}</code>\n\n"
        f"Agar siz admin bo'lsangiz, .env fayliga quyidagini yozing:\n"
        f"<code>ADMIN_ID={message.from_user.id}</code>",
        parse_mode="HTML"
    )
