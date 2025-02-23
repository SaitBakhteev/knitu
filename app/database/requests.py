import logging
from time import time
from aiogram.fsm.context import FSMContext



from config import (TOKEN, DB_USER, DB_PASS,
                    DB_HOST, DB_PORT, DB_NAME)
from tortoise import Tortoise

from tortoise.exceptions import DoesNotExist
from datetime import datetime, timedelta

from app.database.models import User, Category, Question, Survey
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

async def create_category(data):  # создание категории вопроса
    try:
        await Category.create(title=data['title'],
                              animals=data['animals'])
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return

async def create_question(data):
    try:
        category = await Category.get(id=int(data['category_id']))
        await Question.create(text=data['text'],
                              category=category,
                              answers=data['answers'],
                              image_path=data['image_path'],
                              animal=data['animal'])
    except DoesNotExist:
        logger.error(f"Category does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return

async def create_answer(data):
    try:
        question = await Category.get(id=int(data['question_id']))
        await Question.create(text=data['text'],
                              question=question,
                              is_correct=data['is_correct'])
    except DoesNotExist:
        logger.error(f"Question does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return

async def create_survey(data):
    try:
        user = await User.get(tg_id=int(data['user_tg_id']))
        await Question.create(user=user,
                              result=data['result'])
    except DoesNotExist:
        logger.error(f"Question does not exist")
    except Exception as e:
        logger.error(f"Error creating questions: {e}")
        return


''' ПОЛУЧЕНИЕ ОБЪЕКТОВ МОДЕЛЕЙ '''
async def get_user(tg_id=None) -> User():
    try:
        return await User.get(tg_id=tg_id) if tg_id else await User.all()
    except DoesNotExist:
        logger.error(f"User does not exist")
        return

async def get_category(id=None) -> Category():
    try:

        return await Category.get(id=id) if id else await Category.all()

    except DoesNotExist:
        logger.error(f"Category does not exist")
        return

async def get_question(id=None) -> Question():
    try:
        return await Question.get(id=id) if id else await Question.all()
    except DoesNotExist:
        logger.error(f"Question does not exist")
        return


async def get_survey(user: User = None, id=None) -> Survey():
    try:
        if user:
            return await Survey.filter(user=user).all().exists()
        else:
            return await Survey.get(id=id) if id else await Survey.all()

    except DoesNotExist:
        logger.error(f"Question does not exist")
        return



''' ЗАПРОС К БД И РАНДОМНАЯ ГЕНЕРАЦИЯ СПИСКА 
ВОПРОСОВ ДЛЯ ВИКТОРИНЫ '''
async def create_question_list_for_quiz():
    try:
        # извлечение id последней записи в модели Questions
        last_id = await Question.all().order_by('-id').first().values('id')
        logger.info(f"last_id_init = {last_id}")
        last_id = last_id['id']

        # Рандомная генерация списка id вопросов
        _id = randint(1, last_id)
        questions_count, question_id_list = 11, [_id]
        for i in range(questions_count):
            while (_id in question_id_list):
                _id = randint(1, last_id)
            question_id_list.append(_id)
        logger.info(f"question_id_list = {question_id_list}")
        initDB_question_list = await (
            Question.filter(id__in=question_id_list).prefetch_related('category').
            values('id', 'category__title', 'text','answers', 'animal',
                   'image_path'))
        return initDB_question_list
    except Exception as e:
        logger.error(f'ERR = {e}')

# Для тестирования
async def test_request():
    begin = time()
    # survey = await Survey.all().order_by('-id').first().values('id', 'result')
    cat = await Category.filter(id__in=range(4,30)).values()
    query_time = str((time() - begin)*(10**3))
    # return (f'query_time = {query_time};\n'
    #         f'survey_id = {survey['id']};\n'
    #         f'survey_result = {survey['result']}')

    for i in cat:
        logger.info(f'obj = {i}')
    logger.info(f'len = {len(cat)}')
    return 'sdfsdf'