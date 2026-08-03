import json
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
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
    
    await message.answer(
        f"Xush kelibsiz, {message.from_user.full_name}! Quyidagi tugma orqali menyuni ochishingiz mumkin.",
        reply_markup=get_webapp_keyboard()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "Menyu bilan tanishish va buyurtma berish uchun quyidagi tugmani bosing:",
        reply_markup=get_webapp_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Bu restoran botidir.\n\n"
        "Barcha taomlarni ko'rish va xarid qilish uchun chap burchakdagi 🍔 Menyu tugmasidan foydalaning.\n\n"
        "Buyurtmani tasdiqlaganingizdan so'ng sizdan telefon raqamingiz va lokatsiyangizni yuborish so'raladi.\n"
        "Agar xatolik kuzatilsa /start ni bosing.\n\n"
        "📞 Bog'lanish va yordam uchun raqam: +998 88 732 55 15"
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
