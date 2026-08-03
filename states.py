from aiogram.fsm.state import State, StatesGroup

class CheckoutState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_location = State()
    waiting_for_receipt = State()
