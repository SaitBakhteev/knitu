import logging

import asyncio
import time

from typing import Callable, Any, Dict, Awaitable

from aiogram import Router, F, BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.administrator.keyboards import admin_panel_kb
import app.states as st
from config import STUDENT_CF, DENSITY
import app.database.requests as db_req
import app.user.keyboards as kb


logger = logging.getLogger(__name__)

user = Router()

# Кэш список пользователей и дедлайнов
user_cache, dedlines, dedline_notifications = dict(), [], []

# Мидлварь для проверки регистрации пользователя
class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем, является ли пользователь администратором
        if isinstance(event, (Message, CallbackQuery)):
            user_tg_id = event.from_user.id

            ''' Здесь несколько нелогичный код, он чисто для перестраховки, если вдруг
            при первом входе что-то пойдет не так при создании пользователя в БД.
            Также перестраховка по поводу перезапуска сервера  '''

            if user_tg_id not in user_cache:
                # Вот это обращение к БД после первой регистрации
                user = await db_req.get_or_create_user(event.from_user)
                if not user:
                    if isinstance(event, CallbackQuery) and event.data == "registration":
                        return await handler(event, data)  # передача управления хандлерам
                    else:
                        await registration(event)
                        return
                user_cache[user_tg_id] = user

        # Передаем управление следующему обработчику
        return await handler(event, data)

user.message.middleware(AdminMiddleware())
user.callback_query.middleware(AdminMiddleware())


# Удаление сообщений
async def delete_message(message: Message):
    try:
        await message.delete()
    except Exception:
        return


# Регистрация
async def registration(event: Message | CallbackQuery):
    username = event.from_user.username
    event_message = event.message if isinstance(event, CallbackQuery) else event
    if username:
        await event_message.answer(
            'Рады приветствовать в нашем чат-боте ИНХН😊.\n'
            "Для того, чтобы воспользоваться этим ботом нажмите на кнопку регистрации.\n"
            "При этом нажимая на кнопку регистрации, Вы соглашаетесь со всеми условиями предоставления "
            'персональных данных своего телеграмм аккаунта и иных условий пользовательского соглашения, '
            'описанных <a href="https://disk.yandex.ru/i/J4i-dcxqrgKCPw"><b>здесь</b></a>.',
            reply_markup=kb.registration_kb)
    else:
        await event_message.answer(
            "Сожалеем, но у Вас отсутствует никнейм (username) телеграмм 🥺\n"
            "ℹ️ Как установить никнейм (username):\n"
            "1. Откройте 'Настройки' Telegram\n"
            "2. Выберите 'Изменить профиль'\n"
            "3. В поле 'Username' укажите желаемый никнейм\n"
            "4. После этого возвращайтесь в бота!☺️"
        )


@user.callback_query(F.data=='registration')
async def registration_callback_query(call: CallbackQuery):
    try:
        async def inner_registration_callback_query():
            await db_req.get_or_create_user(from_user=call.from_user, create_user=True)

            # Частичное дублирование сообщения от start
            text = (
                'Добро пожаловать в наш чат-бот ИНХН ❤️\n'
                f'На данный момент Вы зарегистрировались здесь, как <i><b>{call.from_user.first_name}</b></i>. '
                f'Если хотите поменять своё имя, то перейдите в <b>/prof</b>\n'
                'Здесь Вы можете пройти увлекательную викторину и подробнее ознакомиться '
                'с нашими специальностями☺️\n'
                'Админы могут добавлять вопросы для викторины.\n'
                'Для работы с ботом, выбирайте команды меню слева внизу.\n'
                '↙️'
            )
            await call.message.answer(text, parse_mode='HTML')

        await asyncio.gather(delete_message(call.message), inner_registration_callback_query())
    except Exception as e:
        await call.message.answer('Сожалеем! Что-то пошло не так 🥺')
        logger.error(f'ERROR from registration_callback_query: {e}')


# ----- ОБРАБОТКА /start -----------

@user.message(CommandStart())
async def start(call_mess: Message | CallbackQuery, state: FSMContext):
    call_mess = call_mess.message if isinstance(call_mess, CallbackQuery) else call_mess
    async def inner_start():
        text = (
            'Здесь Вы можете пройти увлекательную викторину и подробнее ознакомиться '
            'с нашими специальностями☺️\n'
            'Админы могут добавлять вопросы для викторины.\n'
            'Для работы с ботом, выбирайте команды меню слева внизу.\n'
            '↙️'
        )
        await call_mess.answer(text)
    await asyncio.gather(delete_message(call_mess), inner_start())


# Админ панель
@user.message(Command('adm'))
async def adm(message: Message):
    async def answer():
        await message.answer('Админ-панель', reply_markup=admin_panel_kb)
    await asyncio.gather(delete_message(message), answer())
