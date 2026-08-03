from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_categories, get_menu_by_category, get_item, add_to_cart
from keyboards.inline import get_categories_keyboard, get_menu_keyboard, get_item_keyboard

router = Router()

@router.message(F.text == "🍴 Menyu")
async def show_categories(message: Message):
    categories = await get_categories()
    if categories:
        await message.answer("Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))
    else:
        await message.answer("Menyu hozircha bo'sh.")

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_callback(callback: CallbackQuery):
    categories = await get_categories()
    await callback.message.edit_text("Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))

@router.callback_query(F.data.startswith("category_"))
async def show_menu(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    menu_items = await get_menu_by_category(category_id)
    if menu_items:
        await callback.message.edit_text("Taomni tanlang:", reply_markup=get_menu_keyboard(menu_items, category_id))
    else:
        await callback.answer("Bu kategoriyada taom yo'q.", show_alert=True)

@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = await get_item(item_id)
    if item:
        text = f"🍔 *{item[2]}*\n\n📝 {item[3]}\n\n💸 Narxi: {item[4]} so'm"
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
    await callback.answer(f"Savatga {quantity} ta qo'shildi!", show_alert=True)
