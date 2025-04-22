from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import (KeyboardButton,
                                    ReplyKeyboardMarkup,
                                    InlineKeyboardBuilder)


async def reliability_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="90", callback_data="reliability_90")
    keyboard.button(text="95", callback_data="reliability_95")
    keyboard.button(text="98", callback_data="reliability_98")
    keyboard.button(text="99", callback_data="reliability_99")
    return keyboard.as_markup()


async def substance_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="H2SO4", callback_data="substance_H2SO4")
    keyboard.button(text="HCl", callback_data="substance_HCl")
    keyboard.button(text="NaOH", callback_data="substance_NaOH")
    return keyboard.as_markup()


async def volumes_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="20", callback_data="volumes_20")
    keyboard.button(text="25", callback_data="volumes_25")
    keyboard.button(text="50", callback_data="volumes_50")
    keyboard.button(text="100", callback_data="volumes_100")
    keyboard.button(text="200", callback_data="volumes_200")
    keyboard.button(text="250", callback_data="volumes_250")
    keyboard.button(text="500", callback_data="volumes_500")
    keyboard.button(text="1000", callback_data="volumes_1000")
    keyboard.adjust(1)
    return keyboard.as_markup()
