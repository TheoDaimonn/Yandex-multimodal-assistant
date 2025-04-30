from aiogram import Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import config

bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class UserStates(StatesGroup):
    waiting_for_approval = State()
    dialog = State()
    feedback = State()

authorized_users = set()
pending_users = {}
ADMIN_ID = None