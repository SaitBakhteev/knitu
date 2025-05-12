from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Панель управления администратора
admin_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать вопрос ❇️', callback_data='add_question')],
    [InlineKeyboardButton(text='Добавить специальность', callback_data='add_specialization')],
    [InlineKeyboardButton(text='Управление списком админов 😎', callback_data='admin_list')],
    ]
)


# Панель управления списком админов

admin_list_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать админа', callback_data='edit_admin')],
    [InlineKeyboardButton(text='Добавить админа', callback_data='add_admin')],
    [InlineKeyboardButton(text='Удалить админа', callback_data='delete_admin')],
])

# Кнопка для вставки шаблона вопроса
async def question_template_kb() -> InlineKeyboardMarkup:
    template = ('Текст вопроса:\n\n'
                'Варианты ответов:\n'
                '-')
    question_template_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Шаблон вопроса', switch_inline_query_current_chat=template)]
    ])

    return question_template_kb


async def choose_department_kb(*args) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for item in args:
        keyboard.add(InlineKeyboardButton(
            text=item[0],
            callback_data=f'department_{item[1]}')
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


async def return_back_kb(text: str, call_data: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=call_data)]
    ])
    return keyboard