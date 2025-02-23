"""  Сначала будут созданы классы, наследуемые от CallbackData.
С помощью этих классов будут фильтpоваться вызовы. Разделение пагинации
будет осуществляться за чет поля prefix класса-наследника CallbackData.
Пример представлен ниже. Данный усложненный подход был вызван тем, что имеет
место ошибочная реакция бота при нажатии кнопок в то время как для них был
прописан другой callback_data. К примеру, кнопка ничего не должна делать,
но при ее нажатии почему-то возникает какое-то событие, прописанное для другой кнопки

class TestCallback(CallbackData, prefix='test'):
    call_prefix: str

async def kb_test():
    keyboard = InlineKeyboardBuilder()
    calback_1, calback_2, calback_3  = (TestCallback(call_prefix='test1'),
                                        TestCallback(call_prefix='test2'),
                                        TestCallback(call_prefix='test3'))
    keyboard.button(text='First test', callback_data=calback_1.pack())
    keyboard.button(text='Second test', callback_data=calback_2.pack())
    keyboard.button(text='Third test', callback_data=calback_3.pack())

    keyboard.adjust(3)
    return keyboard.as_markup()

Отображение информации о текущем объекте при их пагинации
При пагинации важно отметить, что используются два типа индекса объектов:
 1. Переменная current_index - это индекс объекта в списке, извлеченного из БД.
 2. Переменная object_id - это id объекта в самой БД

Функция "show_object" отображает пользовательский ответ в окне переписки телеграмм
вместе с инлайн-кнопками. При этом содержание инлайновой клавиатуры зависит от того,
для каких цедей используется вызываемая функция. Если для опроса, то только кнопка
"Далее", если для пагинации объектов, то соответствующая панель пагинации  """


from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message, FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import logging
loger = logging.getLogger(__name__)


# Классы для отлова вызовов после нажатия кнопки
class PaginationCallbackData(CallbackData, prefix='pagination'):
    call_prefix: str


# class PaginationQuestionsOnQuiz(CallbackData, prefix='quiz'):
#     call_prefix: str


# Формирование панели кнопок для пагинации
async def get_pagination_keyboard(service_pagination: bool=True,
                                  **kwargs) -> InlineKeyboardMarkup:

    prefix, current_index, total_count, apply_text =\
        (kwargs['prefix'], kwargs['current_index'],
         kwargs['total_count'],  kwargs['apply_text'])
    loger.info(f'get_pag_kb:\n'
               f'prefix={prefix}; current_index={current_index};'
               f'total_count={total_count}')
    keyboard = InlineKeyboardBuilder()

    # Формирование объектов PaginationCallbackData
    (callback_data_for_button_prev, callback_data_for_button_next) =\
        (PaginationCallbackData(call_prefix=f'{prefix}__prev'),
         PaginationCallbackData(call_prefix=f'{prefix}__next'))

    # Кнопка "Назад"
    if current_index > 0:
        keyboard.button(
            text="◀️ Назад",
            callback_data=callback_data_for_button_prev.pack()
        )

    # Текущая страница в формате "X/Y"
    keyboard.button(text=f"{current_index + 1}/{total_count}",
                    callback_data='pass')

    # Кнопка "Вперед"
    if current_index < total_count - 1:
        keyboard.button(text="Вперед ▶️", callback_data=callback_data_for_button_next.pack())

    # keyboard.button(text="Отмена", callback_data="return_callback")

    if service_pagination:
        keyboard.button(text=f'{apply_text}', callback_data=f'apply_{prefix}')
    else:
        # keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_{text}_{current_index}'))
        keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_{prefix}'))
    keyboard.adjust(3) if current_index > 0 and current_index < total_count - 1\
        else keyboard.adjust(2)
    return keyboard.as_markup()


# Универсальная функция пользователького вывода панели инструментов пагинации
async def show_object(message: Message, **kwargs):
    await message.delete()

    object_info = kwargs['object_info']
    image_path = kwargs['image_path'] if 'image_path' in kwargs else None
    answers_list = kwargs['answers_list'] if 'answers_list' in kwargs else None

    try:
        # Формирование пользовательского ответа при пагинации или викторине
        if image_path and answers_list:
            keyboard = InlineKeyboardBuilder()
            for i in answers_list:
                call_data = i['is_correct_answer']
                keyboard.button(text=i['answer'], callback_data=f'quiz_{call_data}')
            keyboard.adjust(1)
            keyboard = keyboard.as_markup()

            await message.answer_photo(FSInputFile(image_path),
                                       caption=object_info,
                                       reply_markup=keyboard)
        else:
            keyboard = await get_pagination_keyboard(**kwargs)
            await message.answer(f'<b>{object_info}</b>',
                                 reply_markup=keyboard, parse_mode='HTML')
    except Exception as e:
        loger.error(f'Ошибка модуля show_object: {e}')


async def pagination_handler(callback_query: CallbackQuery,
                             state: FSMContext, **kwargs):

    prefix = kwargs['prefix']
    try:
        direction = callback_query.data
        if callback_query.data.startswith('pagination'):
            # Переменная direction задает в какую сторону изменять значение переменной current_index
            direction = callback_query.data.split(':')[1].split('__')[1]

            # Чтение значения текущего индекса перебираемого объекта
        data = await state.get_data()
        current_index, total_count, object_list =\
            (data.get('current_index'), data.get('total_count'),
             data.get(f'{prefix}_list'))

        new_index = current_index - 1 if direction == "prev" else current_index + 1
        current_index = new_index  # обновляем значение текущего индекса

        # Проверка, не выходит ли current_index за пределы списка объектов
        if current_index > (total_count - 1):
            current_index = total_count - 1
        elif current_index < 0:
            current_index = 0
        await state.update_data(current_index=current_index)

        object_id, object_info = (
            object_list[current_index][f'{prefix}_id'],
            str(object_list[current_index][f'{prefix}_info'])
        )

    # Обновление записи в state по id объекта при пагинации
        image_path = answers_list = None
        if prefix == 'category':
            await state.update_data(category_id=object_id)
        elif prefix == 'animal':
            await state.update_data(animal=object_info)
        elif prefix == 'quiz':
            data = await state.get_data()
            question_list = data.get('question_list')
            image_path=question_list[current_index]['image_path']
            answers_list=question_list[current_index]['answers']

        # Отображаем новый объект
        if prefix != 'quiz':
            await show_object(callback_query.message,
                              object_info=object_info,
                              current_index=current_index,
                              total_count=total_count,
                              **kwargs)
        else:
            await show_object(callback_query.message,
                              object_info=object_info,
                              current_index=current_index,
                              total_count=total_count,
                              answers_list=answers_list,
                              image_path=image_path,
                              **kwargs)


        # Убираем уведомление о нажатии кнопки
        await callback_query.answer()
    except Exception as e:
        loger.error(f'Error from pagination: {e}\n')


# Для тестирования
async def kb_test():
    kb = InlineKeyboardBuilder()
    kb.button(text=f'Тест', callback_data=f'test_b')
    return kb.as_markup()
