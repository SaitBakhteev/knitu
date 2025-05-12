import logging
import asyncio

from typing import Callable, Any, Dict, Awaitable

from tortoise.exceptions import IntegrityError, DoesNotExist
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           Message, CallbackQuery, FSInputFile, TelegramObject)
from aiogram import Router, F, BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import DEPARTMENT

from app import states as st
import app.pagination as pag
from app.pagination import (get_pagination_keyboard, show_object,
                            pagination_handler, PaginationCallbackData)
from app.database import requests as db_req

import app.administrator.keyboards as kb_adm
from app.user.user_queries import delete_message, user_cache


from pprint import pprint
logger = logging.getLogger(__name__)

adm = Router()


simple_admins = {}


# Мидлварь для проверки прав пользователя
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

            data["is_admin"] = user_cache[user_tg_id].is_admin
            data["is_simple_admin"] = True if user_tg_id in simple_admins else False


        #             if isinstance(event, CallbackQuery) and event.data == "registration":
        #                 print(51)
        #                 return await handler(event, data)
        #             else:
        #                 await registration(event)
        #                 return
        #         user_cache[user_tg_id] = user
        #         data["is_admin"] = None
        #
        #         # Здесь возвращаем при первом входе пользователя или перезапуске сервера
        #         return await handler(event, data)
        #     else:
        #         if user_cache[user_tg_id] is None:  # вот это скорее лишний запрос к БД на всякий случай
        #             user_cache[user_tg_id] = await db_req.get_or_create_user(event.from_user)
        #
        #     user = user_cache[user_tg_id]
        #
        #     if user:
        #         data["is_admin"] = True if (event.from_user.username=='Rustambagautdinov'
        #                                     or event.from_user.username=='SaitBakhteev') \
        #             else user.admin_permissions
        #     else:
        #         data["is_admin"] = False
        # # data["is_admin"] = False
        # logger.info(f'event.from_user.username={event.from_user.username}')
        # # Передаем управление следующему обработчику
        # # print(f'user_cache[e] = {user_cache[tg_id]}')
        return await handler(event, data)

adm.message.middleware(AdminMiddleware())
adm.callback_query.middleware(AdminMiddleware())


# Универсальная функция менеджмента глобальной переменной simple_admins
async def global_caches_managment(tg_id: int = None):
    global simple_admins
    if tg_id:
        admin = await db_req.get_admins(tg_id)
        simple_admins[tg_id] = [item.specialization_id for item in admin] if admin else []
    else:
        simple_admins = {}
        admins = await db_req.get_admins()
        tg_id = None
        for item in admins:
            if tg_id != item.user.tg_id:
                tg_id, new_list = item.user.tg_id, []
            new_list.append(item.specialization_id)
            simple_admins[tg_id] = new_list



# Универсальный обработчик возврата назад
@adm.callback_query(F.data.startswith('return'))
async def return_back(call: CallbackQuery, state: FSMContext):
    match call.data.split(':')[1]:
        case 'admin_list': await admin_list(call, state)





''' СОЗДАНИЕ СПЕЦИАЛЬНОСТИ '''

@adm.callback_query(F.data=='add_specialization')
async def add_specialization(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Наберите код и название специальности, и отправьте сообщение боту.\n'
                              'Например:\n'
                              '<i>18.03.01 «Инновационные технологии международных нефтегазовых корпораций»</i>',
                              parse_mode='HTML')
    await state.set_state(st.CreateSpecialization.department)


@adm.message(st.CreateSpecialization.department)
async def choose_department(message: Message, state: FSMContext):
    try:
        if len(message.text) < 5:
            raise ValueError
        await state.update_data(title=message.text)
        await message.answer(
            'Выберите кафедру, к которой относится специальность',
            reply_markup=await kb_adm.choose_department_kb(*DEPARTMENT)
        )
        await state.set_state(st.CreateSpecialization.specialization)
    except ValueError:
        await message.answer('Слишком короткое название. Повторите ввод')
        return


@adm.callback_query(F.data.startswith('department'), st.CreateSpecialization.specialization)
async def create_specialization_finish(call: CallbackQuery, state: FSMContext):
    department = call.data.split('_')[1]

    # Присвоение названия кафедры из callback_data
    department = next(item[0] for item in DEPARTMENT if item[1] == department)
    data = await state.get_data()
    data['department'] = department
    await db_req.create_specialization(data)
    await state.clear()
    await call.message.answer('Специальность добавлена успешно.')

''' КОНЕЦ СОЗДАНИЯ СПЕЦИАЛЬНОСТИ '''

# Управление списком админов

@adm.callback_query(F.data=='admin_list')
async def admin_list(call_mess: CallbackQuery | Message, state: FSMContext):
    call_mess = call_mess.message if isinstance(call_mess, CallbackQuery) else call_mess
    async def inner_admin_list():
        admin_spec = await db_req.get_admins()  # все записи UserSpecialization
        admin_list = [{'admin_id': item.id,  # на самом деле это id записи UserSpecialization
                       'admin_info': f'Админ: <b>{item.user.full_name}</b>\n'
                                     f' Специальность: <i>{item.specialization.title}</i>\n'
                                     f' Кафедра: <i>{item.specialization.department}</i>'}
                      for item in admin_spec]
        admin_id, admin_info, admin_count,  = admin_list[0]['admin_id'],  admin_list[0]['admin_info'], len(admin_list)

        await state.update_data(admin_list=admin_list, current_index=0,
                                total_count=admin_count, admin_id=admin_id)
        await state.set_state(st.EditAdmin.choose_admin)

        await show_object(call_mess, object_info=admin_info,
                          current_index=0, total_count=admin_count,
                          prefix='admin', apply_text='Добавить')

    await asyncio.gather(inner_admin_list(), delete_message(call_mess))

''' Пагинация админов '''

@adm.callback_query(PaginationCallbackData.filter(F.call_prefix.startswith('admin'))
                    and st.EditAdmin.choose_admin)
async def admin_pagination(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data.startswith('pagination'):
        async def inner_admin_pagination():
                await pagination_handler(callback_query, state=state,
                                         prefix='admin',apply_text='Добавить')
        await asyncio.gather(delete_message(callback_query.message), inner_admin_pagination())


    # Обработчик события добавления админа
    if callback_query.data == 'apply_admin':
        async def add_admin():
            spec_list = await db_req.get_specializations()
            text = ''
            for i, item in enumerate(spec_list):
                text += f'<b>{i+1}.</b> {item.department}: <i>{item.title}</i>\n'
            await callback_query.message.answer(f'Специальности:\n{text}\n'
                                                f'Для добавления админа и привязки его к специальности из списка '
                                                f'выше наберите и отправьте сообщение боту в следующем формате:\n'
                                                f'<i>порядковый номер специальности / никнейм</i>\n'
                                                f'<b><i>Пример</i></b>: 3/ivan2005',
                                                reply_markup=await kb_adm.return_back_kb('Отменить ⛔️',
                                                                                         'return:admin_list'))
            await state.update_data(spec_list=spec_list)
            await state.set_state(st.EditAdmin.add_admin)
        await asyncio.gather(add_admin(), delete_message(callback_query.message))

    # Обработчик события удаления админа
    elif callback_query.data == 'delete_admin':
        async def inner_delete_admin():
            data = await state.get_data()
            admin_list, current_index = data['admin_list'], data['current_index']
            user_spec_id = admin_list[current_index]['admin_id']  # получаем id записи UserSpecialization
            await state.update_data(user_spec_id=user_spec_id)
            await state.set_state(st.EditAdmin.delete_admin)
            await callback_query.message.answer(
                'Введите и отправьте сообщение <i>"да"</i> или отмените процесс',
                parse_mode='HTML',
                reply_markup=await kb_adm.return_back_kb('Отменить ⛔️','return:admin_list')
            )
        await asyncio.gather(delete_message(callback_query.message), inner_delete_admin())


@adm.message(st.EditAdmin.delete_admin)
async def delete_admin(message: Message, state: FSMContext):
    try:
        if message.text.lower() == 'да':
            data = await state.get_data()
            user_spec_id = data['user_spec_id']
            await db_req.delete_user_specialization(user_spec_id)
            await global_caches_managment()  # переобновление кэна simple_admins
        else:
            await message.answer('Удаление отменено')
        await admin_list(message, state)
    except Exception as e:
        logger.error(f'Ошибка в delete_admin: {e}')


@adm.message(st.EditAdmin.add_admin)
async def add_admin_state(message: Message, state: FSMContext):
    try:
        init_input = message.text.split('/')
        process_input = list(map(lambda x: x.strip().replace('@', ''), init_input))
        print(f'init_input = {init_input}\n'
              f'process_input = {process_input}')
        data = await state.get_data()
        spec_list = data['spec_list']
        spec_index = int(process_input[0]) - 1  # индекс объекта из списка spec_list
        user = await db_req.get_user(process_input[1])
        user_id, spec_id = user.id, spec_list[spec_index].id
        await db_req.create_user_specializaton(user_id, spec_id)
        await global_caches_managment()  # переобновление кэна simple_admins
        await message.answer('Новая привязка "<i>Админ-Специальность</i>" добавлена успешно', parse_mode='HTML')
        await admin_list(message, state)
        return
    except IntegrityError:
        text = 'Такая привязка <u>админ-специальность</u> уже существует'
    except DoesNotExist as e:
        if str(e) == 'Object "User" does not exist':
            text = 'Среди пользователей бота такой никнейм не найден'
    except IndexError:
        text = 'Специальность с таким порядковым номером отсутствует'
    except ValueError:
        text = ('Нарушен формат ввода. Нужно вводить в формате <u>номер специальности из списка'
                '/никнейм пользователя</u>')
    except Exception:
        text = ('Возникла неизвестная ошибка')
    await message.answer(f'{text}. Повторите ввод или отмените процесс', parse_mode='HTML',
                         reply_markup=await kb_adm.return_back_kb('Отменить ⛔️', 'return:admin_list'))


''' СОЗДАНИЕ ВОПРОСA '''

@adm.callback_query(F.data=='add_question')
async def add_question_begin(call: CallbackQuery, state: FSMContext, is_simple_admin: bool, is_admin: bool):
    async def inner_add_question_begin():
        await state.clear()
        if is_simple_admin is False and is_admin is False:
            await call.message.answer('У Вас нет прав на совершение данной операции')
            return

        specializations = await db_req.get_specializations(call.from_user.id)
        text = ''
        for i, specialization in enumerate(specializations):
            text += (f'<b>{i+1}</b>. <i>Специальность</i>: {specialization.specialization.title}\n'
                     f'<i>Кафедра</i>: {specialization.specialization.department}\n\n')

        await call.message.answer (
            f'Укажите порядковый номер специальности, к которой хотите '
            f'привязать вопрос викторины:\n'
            f'{text}')
        await state.update_data(specializations=specializations)
    await asyncio.gather(delete_message(call.message), inner_add_question_begin())

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


@adm.message(Command('test'))
async def test_call(message: Message, is_simple_admin: bool):

    print(is_simple_admin)