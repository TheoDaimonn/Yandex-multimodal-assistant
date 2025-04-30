from src.telegram_bot.app.handlers.help import router as help_router
from src.telegram_bot.app.handlers.start import router as start_router
from src.telegram_bot.app.handlers.end import router as end_router

routers = [
    end_router,
    help_router,
    start_router, 
]