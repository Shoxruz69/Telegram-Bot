import html
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from database.db import get_categories, get_menu_by_category, get_item, add_to_cart, get_tenant_by_bot_token
from keyboards.inline import get_categories_keyboard, get_menu_keyboard, get_item_keyboard

router = Router()

async def resolve_tenant(bot: Bot, tenant: dict = None) -> dict:
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
        logging.warning(f"resolve_tenant in menu error: {ex}")
    return {'id': 1, 'name': 'Cafe Express', 'slug': 'express'}

@router.message(F.text == "🍴 Menyu")
async def show_categories(message: Message, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    categories = await get_categories(tenant_id)
    if categories:
        await message.answer("Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))
    else:
        await message.answer("Menyu hozircha bo'sh.")

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_callback(callback: CallbackQuery, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    categories = await get_categories(tenant_id)
    await callback.message.edit_text("Kategoriyani tanlang:", reply_markup=get_categories_keyboard(categories))

@router.callback_query(F.data.startswith("category_"))
async def show_menu(callback: CallbackQuery, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    category_id = int(callback.data.split("_")[1])
    menu_items = await get_menu_by_category(category_id, tenant_id)
    if menu_items:
        await callback.message.edit_text("Taomni tanlang:", reply_markup=get_menu_keyboard(menu_items, category_id))
    else:
        await callback.answer("Bu kategoriyada taom yo'q.", show_alert=True)

@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    item_id = int(callback.data.split("_")[1])
    item = await get_item(item_id, tenant_id)
    if item:
        item_name = html.escape(item[2] or "Taom")
        item_desc = html.escape(item[3] or "")
        item_price = f"{item[4]:,} so'm"
        text = f"🍔 <b>{item_name}</b>\n\n📝 {item_desc}\n\n💸 Narxi: <b>{item_price}</b>"
        await callback.message.delete()
        if item[5] and item[5].startswith("http"):
            try:
                await callback.message.answer_photo(
                    photo=item[5],
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=get_item_keyboard(item_id, item[1], quantity=1)
                )
                return
            except Exception:
                pass
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_item_keyboard(item_id, item[1], quantity=1)
        )

@router.callback_query(F.data.startswith("plus_") | F.data.startswith("minus_"))
async def change_quantity(callback: CallbackQuery, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    action, item_id, quantity = callback.data.split("_")
    item_id = int(item_id)
    quantity = int(quantity)
    
    if action == "plus":
        quantity += 1
    elif action == "minus" and quantity > 1:
        quantity -= 1
        
    item = await get_item(item_id, tenant_id)
    if item:
        await callback.message.edit_reply_markup(reply_markup=get_item_keyboard(item_id, item[1], quantity))

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart_callback(callback: CallbackQuery, bot: Bot, tenant: dict = None):
    cur_tenant = await resolve_tenant(bot, tenant)
    tenant_id = cur_tenant.get('id', 1)
    _, item_id, quantity = callback.data.split("_")
    item_id = int(item_id)
    quantity = int(quantity)
    
    await add_to_cart(callback.from_user.id, item_id, quantity, tenant_id)
    await callback.answer(f"Savatga {quantity} ta qo'shildi!", show_alert=True)
