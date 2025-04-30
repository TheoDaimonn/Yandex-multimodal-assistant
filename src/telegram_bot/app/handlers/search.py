# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from aiogram.enums import ParseMode
# from aiogram.filters import StateFilter
# import logging
# import json
# import ast
# from app.handlers.admin import is_admin
# from app.utils.fix_url import fix_url
# import src.LLMAgent as LLMAgent
# from app.config import WIKI_AGENT_PARAMS
# from app.loader import UserStates, authorized_users
# from app.utils.keyboards import create_feedback_keyboard
# from app.utils.log import log_request
#
# router = Router()
# router.name = 'search'
#
# agent  = LLMAgent.QueryModel(WIKI_AGENT_PARAMS['prompt'], WIKI_AGENT_PARAMS['llm_params'])
#
# @router.message(StateFilter(UserStates.dialog), ~F.text.startswith('/'))
# async def handle_search(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     current_state = await state.get_state()
#
#     logging.info(f"handle_search: user_id={user_id}, current_state={current_state}, in authorized_users={user_id in authorized_users}")
#
#     if user_id not in authorized_users and not await is_admin(user_id, message.from_user.username):
#         await message.answer("У вас нет доступа к поиску. Обратитесь к администратору.")
#         return
#
#
#     query = message.text
#     search_message = await message.answer("🔍 Поиск информации, пожалуйста, подождите...")
#
#     try:
#         model_response = await agent.send_request_async(query)
#     except Exception as e:
#         logging.error(f'Ошибка при запросе к модели: {e}')
#         await search_message.edit_text("❌ Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")
#         return
#
#     if not model_response:
#         await search_message.edit_text("❌ Ничего не найдено по вашему запросу")
#         return
#
#     if isinstance(model_response, dict) and "error" in model_response:
#         error_message = model_response.get("answer", "Произошла ошибка при обработке запроса")
#         await search_message.edit_text(f"❌ {error_message}")
#         return
#
#     if isinstance(model_response, str):
#         try:
#             model_response = json.loads(model_response.replace('```json', '').replace('```', '').strip())
#         except json.JSONDecodeError:
#             try:
#                 model_response = ast.literal_eval(model_response)
#             except (SyntaxError, ValueError):
#                 await search_message.edit_text("❌ Ошибка обработки ответа от модели")
#                 return
#
#     if not isinstance(model_response, list):
#         if isinstance(model_response, dict) and "theme" in model_response and "buttons" in model_response:
#             model_response = [model_response]
#         else:
#             await search_message.edit_text("❌ Некорректный формат ответа от модели")
#             return
#
#     for theme_data in model_response:
#         if not isinstance(theme_data, dict):
#             continue
#
#         buttons = theme_data.get("buttons", [])
#         if not isinstance(buttons, list):
#             theme_data["buttons"] = []
#             continue
#
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=theme_data.get("theme", "Нет названия"), callback_data=f"theme_{i}")]
#         for i, theme_data in enumerate(model_response)
#     ])
#
#     await state.update_data(model_response=model_response, query=query)
#
#     sent_message = await search_message.edit_text(
#         f"📚 <b>Выберите подходящую категорию:</b>",
#         reply_markup=keyboard,
#         parse_mode=ParseMode.HTML
#     )
#     await state.update_data(message_id=sent_message.message_id)
#
#     feedback_data = {
#         "query": query,
#         "model_response": model_response
#     }
#     await state.update_data(feedback_data=feedback_data)
#     log_request(query, model_response, message.from_user)
#
#     await message.answer("Пожалуйста, оцените результаты поиска:", reply_markup=create_feedback_keyboard())
#
# @router.callback_query(StateFilter(UserStates.dialog), F.data.startswith('theme_'))
# async def process_theme_button(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer()
#     theme_index = int(callback_query.data.split('_')[1])
#
#     user_data = await state.get_data()
#     model_response = user_data.get('model_response')
#     message_id = user_data.get('message_id')
#
#     if not model_response or theme_index >= len(model_response):
#         await callback_query.message.answer("Тема не найдена.")
#         return
#
#     selected_theme = model_response[theme_index]
#     theme_name = selected_theme.get("theme", "Нет названия")
#     buttons = selected_theme.get("buttons", [])
#
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(
#             text=f"{'📄' if b.get('content_type') == 'file' else '🔗' if b.get('content_type') == 'link' else '📝'} {b.get('button_name', 'Нет названия')}",
#             callback_data=f"button_{theme_index}_{i}"
#         )] for i, b in enumerate(buttons)
#     ] + [[InlineKeyboardButton(text="↩️ Назад к темам", callback_data="back_to_themes")]])
#
#     await callback_query.message.edit_text(
#         f"📚 Категория: {theme_name}\n <b>Выберите материал из перечня:</b>",
#         reply_markup=keyboard,
#         parse_mode=ParseMode.HTML
#     )
#
# @router.callback_query(StateFilter(UserStates.dialog), F.data.startswith('button_'))
# async def process_button_click(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer()
#
#     user_data = await state.get_data()
#     model_response = user_data.get('model_response')
#     message_id = user_data.get('message_id')
#
#     theme_index, button_index = map(int, callback_query.data.split('_')[1:3])
#     selected_theme = model_response[theme_index]
#     selected_button = selected_theme["buttons"][button_index]
#
#     content = selected_button.get("content", "")
#     content_type = selected_button.get("content_type", "text")
#     content_name = selected_button.get("content_name", "")
#     parent = selected_button.get("parent", "")
#     parent_name = selected_button.get("parent_name", "")
#     theme_name = selected_theme.get("theme", "Нет названия")
#     button_name = selected_button.get("button_name", "Нет названия")
#
#     response_parts = [f"<b>Категория:</b> {theme_name}"]
#
#     if content_type == "text":
#         response_parts.append(f"<b>{button_name}</b>")
#         response_parts.append(content[:500] + ("..." if len(content) > 500 else ""))
#     elif content_type == "link":
#         response_parts.append(f"<b>{button_name}</b>")
#         response_parts.append(f"🔗 <b>Найденная ссылка:</b> <a href='{fix_url(content)}'>{content_name or 'Открыть ссылку'}</a>")
#     elif content_type == "file":
#         response_parts.append(f"<b>{button_name}</b>")
#         response_parts.append(f"📄 <b>Найденный документ:</b> <a href='{fix_url(content)}'>{content_name or content.split('/')[-1]}</a>")
#
#     if parent:
#         response_parts.append(f"📌 <b>Источник на Wiki:</b> <a href='{fix_url(parent)}'>{parent_name or 'Раздел Wiki'}</a>")
#
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(
#             text=f"{'▶️ ' if i == button_index else ''}{'📄' if b.get('content_type') == 'file' else '🔗' if b.get('content_type') == 'link' else '📝'} {b.get('button_name', 'Нет названия')}",
#             callback_data=f"button_{theme_index}_{i}"
#         )] for i, b in enumerate(selected_theme.get("buttons", []))
#     ] + [[InlineKeyboardButton(text="↩️ Назад к темам", callback_data="back_to_themes")]])
#
#     try:
#         await callback_query.message.edit_text(
#             "\n\n".join(response_parts),
#             reply_markup=keyboard,
#             parse_mode=ParseMode.HTML,
#             disable_web_page_preview=False
#         )
#     except Exception as e:
#         logging.error(f"Ошибка при редактировании сообщения: {e}")
#         await callback_query.message.edit_text(
#             f"<b>Тема:</b> {theme_name}\n\n<b>{button_name}</b>\n\n<a href='{content}'>Открыть содержимое</a>",
#             reply_markup=keyboard,
#             parse_mode=ParseMode.HTML
#         )
#
# @router.callback_query(StateFilter(UserStates.dialog), F.data == "back_to_themes")
# async def back_to_themes(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.answer()
#
#     user_data = await state.get_data()
#     model_response = user_data.get('model_response')
#     message_id = user_data.get('message_id')
#
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=theme_data.get("theme", "Нет названия"), callback_data=f"theme_{i}")]
#         for i, theme_data in enumerate(model_response)
#     ])
#
#     await callback_query.message.edit_text(
#         "📚 <b>Выберите подходящую категорию:</b>",
#         reply_markup=keyboard,
#         parse_mode=ParseMode.HTML
#     )
