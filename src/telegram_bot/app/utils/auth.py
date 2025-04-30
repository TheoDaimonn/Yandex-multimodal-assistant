import os
import logging
import json
from app.config import AUTH_USERS_FILE
from app.loader import authorized_users, ADMIN_ID  

def save_authorized_users():
    os.makedirs(os.path.dirname(AUTH_USERS_FILE), exist_ok=True)
    data = {
        "authorized_users": list(authorized_users),
        "admin_id": ADMIN_ID
    }
    with open(AUTH_USERS_FILE, 'w') as f:
        json.dump(data, f)
    logging.info(f"Сохранено {len(authorized_users)} авторизованных пользователей")


def load_authorized_users():
    global ADMIN_ID
    if not os.path.exists(AUTH_USERS_FILE):
        logging.info("Файл с авторизованными пользователями не найден")
        return
    try:
        with open(AUTH_USERS_FILE, 'r') as f:
            data = json.load(f)
        authorized_users.clear()
        authorized_users.update(data.get("authorized_users", []))
        ADMIN_ID = data.get("admin_id")
        logging.info(f"Загружено {len(authorized_users)} авторизованных пользователей")
        if ADMIN_ID:
            logging.info(f"Загружен ID администратора: {ADMIN_ID}")
    except Exception as e:
        logging.error(f"Ошибка при загрузке авторизованных пользователей: {e}")
