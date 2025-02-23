from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import (KeyboardButton,
                                    ReplyKeyboardMarkup,
                                    InlineKeyboardBuilder)

from app.database import requests as db_req


# Клавиатура для регистрации пользователя при первом входе в бот
async def registration_keyboard_on_start() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Регистрация', callback_data='registration')
    return keyboard.as_markup()

async def me_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Я админ этого бота')]])



#
# # клавиатуры для сообщений
# start_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Добавить Авто", callback_data="car_add_callback")]
#     ]
# )
#
# return_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Отмена", callback_data="return_callback")]
#     ]
# )
# skip_menu_kb = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Меню')]
#     ],
#                               resize_keyboard=True,
#                               input_field_placeholder="Выберите пункт меню.",)
#
#
# main_kb = ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text="Избранное")],
#         [KeyboardButton(text="Создать заметку о расходах")],
#         [KeyboardButton(text="Создать Напоминание")],
#         [KeyboardButton(text="Автомобили")]
#     ],
#                               resize_keyboard=True,
#                               input_field_placeholder="Выберите пункт меню.",)
#
# favorites_kb = ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text="Мои товары")],
#         [KeyboardButton(text="Добавить товар в избранное")],
#         [KeyboardButton(text='Меню')]
#     ],
#                                    resize_keyboard=True,
#                                    input_field_placeholder="Выберите пункт меню.",)
#
#
# async def profile_kb(tg_id):
#     cars = await get_all_user_cars(tg_id)
#     keyboard = InlineKeyboardBuilder()
#     for car in cars:
#         brand = car["brand"]
#         model = car["model"]
#         keyboard.add(InlineKeyboardButton(text=f"{brand} {model}", callback_data=f'car_{brand}_{model}'))
#     keyboard.add(InlineKeyboardButton(text="Список покупок", callback_data='list_purchases'))
#     keyboard.add(InlineKeyboardButton(text='Все записи о ТО', callback_data = 'list_service'))
#     keyboard.add(InlineKeyboardButton(text="Меню", callback_data="return_callback"))
#     return keyboard.adjust(1).as_markup()
#
# settings_kb = ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text="Удалить Авто"),KeyboardButton(text="Добавить Авто")],
#         [KeyboardButton(text='Удалить заметку'),KeyboardButton(text='Удалить напоминание')],
#         [KeyboardButton(text='Меню')]
#
#     ],
#                                   resize_keyboard=True,
#                                   input_field_placeholder="Выберите пункт меню.",)
#
# async def all_cars_kb(tg_id):
#     cars = await get_all_user_cars(tg_id)
#     keyboard = ReplyKeyboardBuilder()
#     for car in cars:
#         brand = car["brand"]
#         model = car["model"]
#         keyboard.add(KeyboardButton(text=f"{brand} {model}"))
#     keyboard.add(KeyboardButton(text="Отмена"))
#     return keyboard.adjust(1).as_markup(resize_keyboard=True)
#
#
# add_service_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="Добавить сервис", callback_data="add_service")]
#     ]
# )
#
# async def services_kb():
#     keyboard = InlineKeyboardBuilder()
#     for service in TYPE_CHOICES:
#         keyboard.add(InlineKeyboardButton(text=f'{service}', callback_data='asda'))
#     return keyboard.adjust(1).as_markup()
#
# skip_kb = ReplyKeyboardMarkup(keyboard=[
#         [KeyboardButton(text="пропустить")],
#         [KeyboardButton(text="Меню")]
# ],      resize_keyboard=True,
#         input_field_placeholder="Напишите или выберите 'пропустить'",)
#
# # Функция для создания клавиатуры пагинации для покупок
# async def get_pagination_keyboard(current_index, total_count, text):
#     keyboard = InlineKeyboardBuilder()
#
#     # Кнопка "Назад"
#     if current_index > 0:
#         keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"prev_{current_index}"))
#     else:
#         keyboard.add(InlineKeyboardButton(text=" ", callback_data="ignore"))  # Пустая кнопка
#
#     # Текущая страница в формате "X/Y"
#     keyboard.add(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="page_info"))
#
#     # Кнопка "Вперед"
#     if current_index < total_count - 1:
#         keyboard.add(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"next_{current_index}"))
#     else:
#         keyboard.add(InlineKeyboardButton(text=" ", callback_data="ignore"))  # Пустая кнопка
#
#     keyboard.add(InlineKeyboardButton(text="В меню", callback_data="return_callback"))
#     keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_{text}_{current_index}'))
#     keyboard.adjust(3)
#     return keyboard.as_markup()
#
# async def delete_user_notes_kb(tg_id):
#     keyboard = InlineKeyboardBuilder()
#     notes = await get_user_notes(tg_id)
#     notes_list = notes.split('\n')
#
#     for note in notes_list:
#         text = note.split(' ')[2]
#
#         keyboard.add(InlineKeyboardButton(text=note, callback_data=f'note_{text}'))
#
#     keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="return_callback"))
#     return keyboard.adjust(1).as_markup()
#
# async def delete_user_reminders_kb(tg_id):
#     reminders = await get_user_reminders(tg_id)
#     keyboard = InlineKeyboardBuilder()
#     for reminder in reminders:
#         text = f"{reminder.text} - {reminder.total_date}"
#         keyboard.add(InlineKeyboardButton(text=text, callback_data=f'reminder_{reminder.text}&{reminder.total_date}'))
#
#     keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="return_callback"))
#     return keyboard.adjust(1).as_markup()
#
# async def confirmation_delete_kb(text, current_index):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text='Удалить!',callback_data=f'del_{text}'))
#     keyboard.add(InlineKeyboardButton(text="Назад.", callback_data=f"next_{current_index}"))
#     return keyboard.adjust(1).as_markup()
#
# async def confirm_add_serv_kb(type):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text='Подтвердить!', callback_data=f'confirm_add_{type}'))
#     keyboard.add(InlineKeyboardButton(text='Отмена',callback_data='return_callback'))
#     return keyboard.adjust(1).as_markup()
#
# async def get_pagination_keyboard_service(current_index, total_count):
#     keyboard = InlineKeyboardBuilder()
#
#     # Кнопка "Назад"
#     if current_index > 0:
#         keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"ps_{current_index}"))
#     else:
#         keyboard.add(InlineKeyboardButton(text=" ", callback_data="ignore"))  # Пустая кнопка
#
#     # Текущая страница в формате "X/Y"
#     keyboard.add(InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="page_info"))
#
#     # Кнопка "Вперед"
#     if current_index < total_count - 1:
#         keyboard.add(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"ns_{current_index}"))
#     else:
#         keyboard.add(InlineKeyboardButton(text=" ", callback_data="ignore"))  # Пустая кнопка
#
#     keyboard.add(InlineKeyboardButton(text="В меню", callback_data="return_callback"))
#     keyboard.add(InlineKeyboardButton(text='Зафиксировать виды работ', callback_data='apply_service'))
#
#     keyboard.adjust(3)
#     return keyboard.as_markup()
