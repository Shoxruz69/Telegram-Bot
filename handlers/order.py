import os
from aiogram import Router, Bot
from aiogram.types import Message
from database.db import get_cart, clear_cart, get_user, create_order, get_tenant_by_bot_token
from keyboards.reply import get_webapp_keyboard
from dotenv import load_dotenv

load_dotenv()

router = Router()

def get_all_admin_ids(tenant=None):
    ids = []
    candidates = []
    if tenant and isinstance(tenant, dict):
        val = tenant.get('admin_telegram_id')
        if val:
            candidates.append(str(val))
    env_admin = os.getenv("ADMIN_ID", "")
    if env_admin:
        candidates.append(str(env_admin))
    for cand in candidates:
        if not cand or any(ph in str(cand).upper() for ph in ['YOUR_', '_HERE', 'NONE', 'NULL']):
            continue
        for part in str(cand).replace(";", ",").replace(" ", ",").split(","):
            part = part.strip()
            if part.isdigit() and int(part) > 1000:
                int_id = int(part)
                if int_id not in ids:
                    ids.append(int_id)
    return ids


async def finalize_order(message: Message, payment_method: str = "Aniqlanmadi", receipt_image: str = None):
    bot: Bot = message.bot
    tenant = getattr(bot, 'tenant', None)
    if not tenant:
        tenant = await get_tenant_by_bot_token(bot.token)
    tenant_id = tenant['id'] if tenant else 1
    tenant_slug = tenant['slug'] if tenant else "express"
    admin_ids = get_all_admin_ids(tenant)

    user_id = message.from_user.id
    cart_items = await get_cart(user_id, tenant_id=tenant_id)
    
    if not cart_items:
        await message.answer("Savatingiz bo'sh!", reply_markup=get_webapp_keyboard(user_id, tenant_slug=tenant_slug))
        return
        
    user = await get_user(user_id, tenant_id=tenant_id)
    if not user or not user[1]:
        await message.answer("Foydalanuvchi ma'lumotlari to'liq emas. /start ni bosing", reply_markup=get_webapp_keyboard(user_id, tenant_slug=tenant_slug))
        return
        
    phone = user[1]
    
    # Ma'lumotlar bazasiga buyurtmani saqlash
    order_id = await create_order(user_id, payment_method, receipt_image, tenant_id=tenant_id)
    
    order_text = f"🆕 YANGI BUYURTMA #{order_id}!\n\n👤 Mijoz: {message.from_user.full_name}\n📞 Tel: {phone}\n💳 To'lov turi: {payment_method}\n📄 Holat: Kutilmoqda\n\nBuyurtma tarkibi:\n"
    total_sum = 0
    
    for _, name, _, qty, total in cart_items:
        order_text += f"- {name} x {qty} = {total} so'm\n"
        total_sum += total
        
    order_text += f"\nJami: {total_sum} so'm"
    
    for a_id in admin_ids:
        try:
            if receipt_image:
                file_path = os.path.join('static', 'uploads', 'receipts', receipt_image)
                from aiogram.types import FSInputFile
                if os.path.exists(file_path):
                    await bot.send_photo(a_id, FSInputFile(file_path), caption=order_text)
                else:
                    await bot.send_message(a_id, order_text)
            else:
                await bot.send_message(a_id, order_text)
                
            if user[2] and user[3] and user[2] != 0.0:
                await bot.send_location(a_id, latitude=user[2], longitude=user[3])
        except Exception as e:
            print(f"Error sending to admin {a_id}: {e}")
            
    await clear_cart(user_id, tenant_id=tenant_id)
    await message.answer(
        f"✅ Buyurtmangiz #{order_id} qabul qilindi va admin tasdiqlashi kutilmoqda. Tasdiqlanganda sizga xabar beramiz!", 
        reply_markup=get_webapp_keyboard(user_id, tenant_slug=tenant_slug)
    )
