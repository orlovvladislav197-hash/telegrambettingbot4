from aiogram.fsm.state import State, StatesGroup

class BetStates(StatesGroup):
    waiting_for_amount = State()
