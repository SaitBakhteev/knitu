import logging
from time import time
from aiogram.fsm.context import FSMContext



from config import (TOKEN, DB_USER, DB_PASS,
                    DB_HOST, DB_PORT, DB_NAME)
from tortoise import Tortoise

from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

from app.database.models import User
from random import randint, choice, shuffle

logger = logging.getLogger(__name__)


''' СОЗДАНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''
async def create_user(from_user):  # создание пользователя
    try:
        await User.get_or_create(tg_id=from_user.id,
                                 tg_username=from_user.username,
                                 tg_name=from_user.first_name)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return

