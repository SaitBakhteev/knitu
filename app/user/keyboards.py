from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardMarkup,
                                    InlineKeyboardButton)


registration_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='🖍 Регистрация', callback_data='registration'
    )
    ]]
)
