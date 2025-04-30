import datetime
import logging

from aiogram import types


def log_request(query: str, model_response, user: types.User):
    '''все логаем'''
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if model_response:
        results_text = str(model_response)
    else:
        results_text = "Нет результатов"

    log_line = (
        "---------------------------\n"
        f"Timestamp: {timestamp}\n"
        f"Username: {user.username}\n"
        f"Query: {query}\n"
        f"Results:\n{results_text}\n"
        "---------------------------\n\n"
    )

    with open("data/result/request_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

    logging.info(f"Запрос пользователя {user.id} ({user.username}): {query}")
    logging.info(f"Результат: {results_text}")  

# # лог txt + гугл таблицы
# def log_feedback(query: str,model_response, feedback: str, user: types.User):
#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     if model_response:
#         results_text = str(model_response)
#     else:
#         results_text = "Нет результатов"
#
#     log_line = (
#         "---------------------------\n"
#         f"Timestamp: {timestamp}\n"
#         f"User ID: {user.id}\n"
#         f"Username: {user.username}\n"
#         f"Query: {query}\n"
#         f"Results:\n{results_text}\n"
#         f"Feedback: {feedback}\n"
#         "---------------------------\n\n"
#     )
#
#     with open("data/result/feedback_log.txt", "a", encoding="utf-8") as f:
#         f.write(log_line)
#
#     try:
#         scope = [
#             "https://spreadsheets.google.com/feeds",
#             "https://www.googleapis.com/auth/spreadsheets",
#             "https://www.googleapis.com/auth/drive.file",
#             "https://www.googleapis.com/auth/drive"
#         ]
#
#         credentials_file = os.getenv("GSHEET_CREDENTIALS_JSON")
#         spreadsheet_id = os.getenv("GSHEET_ID")
#         sheet_name = os.getenv("GSHEET_SHEET_NAME", "ОС")
#
#         creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
#         client = gspread.authorize(creds)
#         sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
#
#         max_cell_length = 50000
#         if len(str(model_response)) > max_cell_length:
#             model_response_str = str(model_response)[:max_cell_length] + "..."
#         else:
#             model_response_str = str(model_response)
#
#         row = [timestamp, user.id, user.username, query, model_response_str, feedback]
#         sheet.append_row(row)
#
#         logging.info("✅ Feedback успешно записан в Google Sheets")
#     except gspread.exceptions.APIError as e:
#         logging.error("Ошибка API Google Sheets: %s", e)
#     except Exception as e:
#         logging.error("Ошибка логирования в Google Sheets: %s", e)
