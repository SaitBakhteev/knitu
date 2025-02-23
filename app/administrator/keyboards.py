from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
# панель кнопок администратора за пределами окна переписки
admin_panel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Добавить вопрос'),
                                             KeyboardButton(text='Просмотреть вопросы')],
                                            [KeyboardButton(text='Добавить категорию'),
                                             KeyboardButton(text='Просмотреть категорию')]],
                                  resize_keyboard=True)

kb_add_question = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить вопрос', callback_data='add_question' )]])
