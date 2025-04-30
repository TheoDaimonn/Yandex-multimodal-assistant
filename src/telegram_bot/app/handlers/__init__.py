from src.telegram_bot.app.handlers.help import router as help_router
from src.telegram_bot.app.handlers.start import router as start_router

routers = [
    help_router,
    start_router, 
]