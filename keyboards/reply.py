from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_webapp_keyboard():
    # As requested by the user, we no longer use a Web App, 
    # just standard reply keyboards styled for Cafe Express.
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🟣 Menyu"), KeyboardButton(text="🟢 Savat")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="📞 Biz bilan aloqa")]
        ],
        resize_keyboard=True
    )

def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
