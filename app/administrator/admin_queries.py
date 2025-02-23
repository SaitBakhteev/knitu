import logging


from aiogram.enums import ChatAction

from app.user import keyboards as user_kb
from app.pagination import get_pagination_keyboard, show_object, pagination_handler, PaginationCallbackData

import app.pagination as pag

from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           Message, CallbackQuery, FSInputFile)
from aiogram import Router, F

from aiogram.filters.callback_data import CallbackData

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.database import requests as db_req
from app import states as st



from pprint import pprint
logger = logging.getLogger(__name__)

adm = Router()


''' СОЗДАНИЕ КАТЕГОРИИ ВОПРОСОВ'''

@adm.message(F.text=='Добавить категорию')
async def add_test(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Введите название название категории:')
    await state.set_state(st.CreateCategoryFSM.title)

@adm.message(st.CreateCategoryFSM.title)
async def add_test_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Введите список животных этой категории через запятую:')
    await state.set_state(st.CreateCategoryFSM.animals)

@adm.message(st.CreateCategoryFSM.animals)
async def add_test_title(message: Message, state: FSMContext):
    try:
        await state.update_data(animals=message.text.split(','))
        data = await state.get_data()
        await db_req.create_category(data)
        await message.answer(f'Категория <b><i>{data.get('title')}</i></b> '
                             f'добавлена успешно.', parse_mode='HTML')
        await state.clear()
    except:
        await message.answer('Нужно ввести хотя бы одно животное')
        return


''' СОЗДАНИЕ ВОПРОСA '''
@adm.message(F.text=='Добавить вопрос')
async def add_question_begin(message: Message, state: FSMContext):
    await state.clear()
    categories = await db_req.get_category()
    if not categories:
        await message.answer("У вас нет в базе ни одной категории вопроса")
        await state.clear()
    else:
        category_list = [{'category_id': category.id, 'category_info': category} for category in categories]
        category_id = category_list[0]['category_id']
        category_count, category_info = len(category_list), str(category_list[0]['category_info'])
        await state.update_data(category_list=category_list,
                                category_id=category_id,
                                current_index=0, total_count=category_count)
        await message.answer('Выберите категорию вопроса:')
        await show_object(message, object_info=category_info,
                          current_index=0, total_count=category_count,
                          prefix='category', apply_text='Принять категорию')
        await state.set_state(st.CreateQuestionFSM.category)

''' Пагинация категории и выбор категории. Здесь важно отметить, что
не удалось разделить пагинацию и apply_category '''
@adm.callback_query(PaginationCallbackData.filter(F.call_prefix.startswith('category'))
                    and st.CreateQuestionFSM.category)
async def category_pagination(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data.startswith('pagination'):
        # await callback_query.message.delete()
        await pagination_handler(
            callback_query, state=state,
            prefix='category',apply_text='Принять категорию'
        )

    if callback_query.data == 'apply_category':
        data = await state.get_data()
        category_id = data.get('category_id')
        category = await db_req.get_category(category_id)
        await callback_query.message.answer(f'Выбрана категория <b>{str(category)}</b>.\n'
                                   f'Теперь введите название животного, '
                                   f'которому будет посвящен вопрос', parse_mode='HTML')

        # Формирование кнопок для пагинации животных
        animal_list = [{'animal_id': i, 'animal_info': animal}
                       for i, animal in enumerate(category.animals)]
        animal = animal_list[0]['animal_info']
        await show_object(callback_query.message, object_info=animal,
                          current_index=0, total_count=len(animal_list),
                          prefix='animal', apply_text='Принять животное')
        await state.update_data(animal_list=animal_list, animal=animal,
                                current_index=0, total_count=len(animal_list))
        await state.set_state(st.CreateQuestionFSM.animal)


@adm.callback_query(PaginationCallbackData.filter(F.call_prefix.startswith('animal'))
                    and st.CreateQuestionFSM.animal)
async def category_pagination(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data.startswith('pagination'):
        await pagination_handler(
            callback_query, state=state,
            prefix='animal', apply_text='Принять животное'
        )
    if callback_query.data == 'apply_animal':
        try:
            data = await state.get_data()
            animal = data.get('animal')
            await callback_query.message.answer(f'Выбрано животное: {animal}.\n'
                                                f'Теперь введите текст вопроса:')
            await state.set_state(st.CreateQuestionFSM.text)
        except Exception as e:
            logger.error(f'ERROR = {e}')
@adm.message(st.CreateQuestionFSM.text)
async def add_question_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.delete()
    await message.answer('Введите 4 варианта ответов разделяя их через слэш <b><i>"/"</i></b>', parse_mode='HTML')
    await state.set_state(st.CreateQuestionFSM.answers)
#
@adm.message(st.CreateQuestionFSM.answers)
async def add_answers(message: Message, state: FSMContext):
    await state.update_data(answer_text=message.text)
    await message.answer(f'Сформулирован вопрос:\n{message.text}')
    data = await state.get_data()
    try:
        answers_text = str(data.get('answer_text'))
        answers = [{'answer': i, 'is_correct_answer': False}
                   for i in answers_text.split('/')]
        if len(answers) == 4:

            # Запись ответов в виде списка словарей в поле БД JSON-формата
            await state.update_data(answers=answers)

            await state.set_state(st.CreateQuestionFSM.correct_answer)

            # Отображение сформировавшегося вопроса
            show_question_text = (f'<b>{str(data.get('text'))}</b\n>'
                                  f'Варианты ответов:\n'
                                  f'1. {answers[0]['answer']}\n'
                                  f'2. {answers[1]['answer']}\n'
                                  f'3. {answers[2]['answer']}\n'
                                  f'4. {answers[3]['answer']}')
            await message.answer(show_question_text, parse_mode='HTML')
            await message.answer('Введите номер правильного варианта ответа от 1 до 4.')
        else:
            await message.answer('Количество вариантов ответов должно'
                                 ' быть строго 4. Повторите ввод ответов:')
            return
    except:
        await message.answer('Произошла неизвестная ошибка!')
        return
#
# Добавление номера правильного варианта ответа
@adm.message(st.CreateQuestionFSM.correct_answer)
async def last_step_create_question(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get('answers')
    try:
        num = int(message.text)
        answers[num-1]['is_correct_answer'] = True
        data = await state.get_data()
        question_text = str(data.get('text'))
        await message.answer(f"Сформирован вопрос <b>{question_text}</b> "
                             f"с правильным ответом <i>{answers[num-1]['answer']}</i>.",
                             parse_mode='HTML')
        await state.update_data(answers=answers)
        await message.answer('Остался последний шаг, загрузите фото животного:')
        await state.set_state(st.CreateQuestionFSM.image)
    except Exception as e:
        logger.error(f'log_error = {e}')
        await message.answer('Указан неорректный номер правильного ответа, повторите ввод:')
        return

# Последний этап, загрузка и сохранение в БД вопроса в модель Question
@adm.message(st.CreateQuestionFSM.image)
async def load_image_and_finish_create_question(message: Message, state: FSMContext):
    file_name = f"media/{message.chat.id}_{message.photo[-1].file_id}.jpg"
    await message.bot.download(file=message.photo[-1].file_id, destination=file_name)
    await state.update_data(image_path=file_name)
    data = await state.get_data()
    await db_req.create_question(data)
    await state.clear()
    await message.answer('Вопрос сохранен в БД!')


''' ДЛЯ ТЕСТИРОВАНИЯ '''


@adm.message(Command(commands=['tr']))
async def tr(message: Message, state: FSMContext):
    await message.answer('Start_test',
                         reply_markup=await pag.kb_test())
    await state.clear()
    await state.update_data(count=0)

@adm.callback_query(F.data=='test_b')
async def test_b(call: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    await state.set_state(st.QuizFSM.continue_quiz)
    try:
        count = data.get('count')
        count += 1
        await state.set_state(st.QuizFSM.continue_quiz)
        if count<4:
            await state.update_data(count=count)
            await call.answer()
            await continue_quiz(call.message, state)
            logger.info('press test')
        else:
            await state.clear()
            await call.message.answer('End_test')
    except Exception as e:
        logger.error(f'Error = {e}')

@adm.message(st.QuizFSM.continue_quiz)
async def continue_quiz(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get('count')
    logger.info(f'we are in continue_quiz')
    await message.answer(f'Continue_test; '
                         f'step: {step}',
                         reply_markup=await pag.kb_test())

@adm.message(Command('adm'))
async def adm_test(message: Message):
    logger.info(f'is_survey')
