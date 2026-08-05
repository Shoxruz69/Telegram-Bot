from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_categories_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat[1], callback_data=f"category_{cat[0]}")
    builder.adjust(2)
    return builder.as_markup()

def get_menu_keyboard(menu_items, category_id):
    builder = InlineKeyboardBuilder()
    for item in menu_items:
        builder.button(text=f"{item[2]} - {item[4]} so'm", callback_data=f"item_{item[0]}")
    builder.button(text="⬅️ Ortga", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()

def get_item_keyboard(item_id, category_id, quantity=1):
    builder = InlineKeyboardBuilder()
    builder.button(text="➖", callback_data=f"minus_{item_id}_{quantity}")
    builder.button(text=f"{quantity}", callback_data="ignore")
    builder.button(text="➕", callback_data=f"plus_{item_id}_{quantity}")
    builder.button(text="🟢 Savatga qo'shish", callback_data=f"add_{item_id}_{quantity}")
    builder.button(text="⬅️ Ortga", callback_data=f"category_{category_id}")
    builder.adjust(3, 1, 1)
    return builder.as_markup()

def get_cart_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✨ Buyurtmani tasdiqlash", callback_data="confirm_order")
    builder.button(text="🗑 Savatni tozalash", callback_data="clear_cart")
    builder.button(text="⬅️ Menyu", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()
