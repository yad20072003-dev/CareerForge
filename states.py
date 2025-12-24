from aiogram.dispatcher.filters.state import State, StatesGroup

class DialogStates(StatesGroup):
    waiting_input = State()
    waiting_mock_context = State()
    waiting_mock_answer = State()
