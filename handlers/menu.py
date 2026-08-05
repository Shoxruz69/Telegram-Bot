from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_categories, get_menu_by_category, get_item, add_to_cart, get_cart, clear_cart
from keyboards.inline import get_categories_keyboard, get_menu_keyboard, get_item_keyboard, get_cart_keyboard

router = Router()

@router.message(F.text == "🟣 Menyu")
async def show_categories(message: Message):
    categories = await get_categories()
    if categories:
        await message.answer("✨ Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))
    else:
        await message.answer("Menyu hozircha bo'sh. 😔")

@router.message(F.text == "🟢 Savat")
async def show_cart(message: Message):
    cart_items = await get_cart(message.from_user.id)
    if not cart_items:
        await message.answer("Sizning savatingiz bo'sh. 😔")
        return
        
    text = "🛒 *Sizning savatingiz:*\n\n"
    total_sum = 0
    for item in cart_items:
        # item: (id, name, price, quantity, total)
        text += f"🍔 {item[1]} x {item[3]} = {item[4]} so'm\n"
        total_sum += item[4]
        
    text += f"\n💳 *Jami:* {total_sum} so'm"
    await message.answer(text, parse_mode="Markdown", reply_markup=get_cart_keyboard())

@router.callback_query(F.data == "clear_cart")
async def clear_cart_callback(callback: CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.message.edit_text("🗑 Savat tozalandi.")

@router.callback_query(F.data == "confirm_order")
async def confirm_order_callback(callback: CallbackQuery):
    await callback.message.answer("To'lov turini tanlang. (Hozircha faqat Naqd yoki joyida to'lov uchun qilingan). Telefon raqamingizni pastdagi tugma orqali yuboring:", reply_markup=__import__('keyboards.reply', fromlist=['get_contact_keyboard']).get_contact_keyboard())
    # State ga o'tkazish kerak, lekin hozircha oddiy qilamiz.
    from aiogram.fsm.context import FSMContext
    from states import CheckoutState
    state: FSMContext = FSMContext(
        storage=callback.bot.fsm.storage, 
        key=callback.bot.fsm.storage.DefaultKey(
            chat_id=callback.message.chat.id, 
            user_id=callback.from_user.id,
            bot_id=callback.bot.id
        )
    )
    await state.set_state(CheckoutState.waiting_for_phone)

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_callback(callback: CallbackQuery):
    categories = await get_categories()
    await callback.message.edit_text("✨ Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))

@router.callback_query(F.data.startswith("category_"))
async def show_menu(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    menu_items = await get_menu_by_category(category_id)
    if menu_items:
        await callback.message.edit_text("🚀 Taomni tanlang:", reply_markup=get_menu_keyboard(menu_items, category_id))
    else:
        await callback.answer("Bu kategoriyada taom yo'q.", show_alert=True)

@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = await get_item(item_id)
    if item:
        text = f"🟣 *{item[2]}*\n\n📝 {item[3]}\n\n💸 Narxi: *{item[4]} so'm*"
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=item[5],
            caption=text,
            parse_mode="Markdown",
            reply_markup=get_item_keyboard(item_id, item[1], quantity=1)
        )

@router.callback_query(F.data.startswith("plus_") | F.data.startswith("minus_"))
async def change_quantity(callback: CallbackQuery):
    action, item_id, quantity = callback.data.split("_")
    item_id = int(item_id)
    quantity = int(quantity)
    
    if action == "plus":
        quantity += 1
    elif action == "minus" and quantity > 1:
        quantity -= 1
        
    item = await get_item(item_id)
    await callback.message.edit_reply_markup(reply_markup=get_item_keyboard(item_id, item[1], quantity))

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart_callback(callback: CallbackQuery):
    _, item_id, quantity = callback.data.split("_")
    item_id = int(item_id)
    quantity = int(quantity)
    
    await add_to_cart(callback.from_user.id, item_id, quantity)
    await callback.answer(f"🟢 Savatga {quantity} ta qo'shildi!", show_alert=True)
