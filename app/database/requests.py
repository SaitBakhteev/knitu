import logging
from time import time
from aiogram.fsm.context import FSMContext



from config import (TOKEN, DB_USER, DB_PASS,
                    DB_HOST, DB_PORT, DB_NAME)
from tortoise import Tortoise

from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

from app.database.models import User, Specialization, UserSpecialization
from random import randint, choice, shuffle

logger = logging.getLogger(__name__)


# Создание или получение пользователя
async def get_or_create_user(from_user, for_telegramm=False, create_user=False):
    try:
        if for_telegramm:
            return await User.get(tg_id=from_user.id).values('id', 'is_admin')

        user = await User.get_or_none(tg_id=from_user.id)
        if create_user:
            await User.create(
                tg_id=from_user.id, tg_username=from_user.username,
                tg_name=from_user.first_name, full_name=from_user.first_name,
                created_at=datetime.now()
            )
            return
        return user
    except Exception as e:
        logger.error(f"User is not created; {e}")
        return


''' СОЗДАНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''
async def create_user(from_user):  # создание пользователя
    try:
        await User.get_or_create(tg_id=from_user.id,
                                 tg_username=from_user.username,
                                 tg_name=from_user.first_name)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return


async def create_specialization(data):
    try:
        await Specialization.create(title=data['title'], department=data['department'])
    except Exception as e:
        logger.error(f"Error creating specialization: {e}")


async def create_user_specializaton(user_id: int, specialization_id: int):
    await UserSpecialization.create(user_id=user_id, specialization_id=specialization_id)


''' ПОЛУЧЕНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''

async def get_all_users():
    return await User.all()


async def get_admins(tg_id: int = None):
    try:
        if tg_id:
            user = await User.get(tg_id=tg_id)
            return await UserSpecialization.filter(user_id=user.id).all()

        return await (UserSpecialization.all().
                      select_related('user', 'specialization').
                      order_by('user_id'))
    except DoesNotExist as e:
        logger.error(f"ERROR get_admins: {e}")
        return

async def get_user(tg_username: str = None,
                   tg_id: int = None,):
    if tg_username:
        return await User.get(tg_username=tg_username)


async def get_specializations(tg_id=None):
    if tg_id:
        user = await User.get(tg_id=tg_id)
        return await UserSpecialization.filter(user_id=user.id).select_related('specialization').all()
    return await Specialization.all().order_by('department')


''' УДАЛЕНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''

async def delete_user_specialization(id: int):
    await UserSpecialization.filter(id=id).delete()