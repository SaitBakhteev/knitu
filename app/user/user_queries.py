import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import app.user.keyboards as kb_user
import app.states as st
from config import STUDENT_CF, DENSITY
import app.database.requests as db_reg


logger = logging.getLogger(__name__)

user = Router()


# ----- ОБРАБОТКА /start -----------
@user.message(CommandStart())
async def start(message: Message):
    text = ('Рады приветствовать в нашем чат-боте ИНХН😊. '
            'Здесь можете:\n'
            '1. Провести метрологическую оценку результатов измерений.\n'
            '2. Рассчитать рецептуру для приготовления растворов кислот и оснований.\n'
            # '3. И конечно пройти увлекательный опрос-викторину'
            )
    await message.answer(text)


@user.message(Command(commands=['mtr']))
async def begin_metrology(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите надежность",
                         reply_markup=await kb_user.reliability_kb())


@user.callback_query(F.data.startswith('reliability'))
async def reliability_callback(call: CallbackQuery, state: FSMContext):
    reliability = call.data.split('_')[1]
    await state.update_data(reliability=reliability)
    await call.message.answer(f"Вы выбрали надежность {reliability}.\n"
                              "Теперь введите через слеш значения результатов измерений.\n"
                              "Например: <i>0.502/0.504/0.503/0.501/0.505</i>\n"
                              "❗️Число данных должно быть от <b>2 до 10!</b>",
                              parse_mode="HTML")
    await state.set_state(st.MetrologyFSM.measurements)


@user.message(st.MetrologyFSM.measurements)
async def finish_metrology(message: Message, state: FSMContext):
    try:
        text = message.text.replace(" ", "").replace(",", ".").split("/")

        # Переделка списка под числовой формат
        lst = [float(i) for i in text]
        logger.info(lst)
        # Формирование нового списка на всякий случай
        if len(text)>1 and len(text)<11:
            data = await state.get_data()
            reability, n = data["reliability"], len(text)
            student = STUDENT_CF[reability][str(n)]
            n = len(lst)
            average = sum(lst)/n
            sum_dev = sum(map(lambda x: (x-average)**2, lst))
            eps = (sum_dev/(n*(n-1)))**0.5*student
            delta = round((eps/average*100), 2)

            # Опеределение позиций для округления до 3 значащих цифр
            pos_avg = next(i for i, item in enumerate(str(average)) if item!="0" and item!=".") + 1
            pos_eps = next(i for i, item in enumerate(str(eps)) if item!="0" and item!=".") + 1
            average, eps = round(average, pos_avg), round(eps, pos_eps)
            await message.answer(f"Результат измерения: \n"
                                 f"- <b><i>{average}+-{eps}</i></b>;\n"
                                 f"- случайная погрешность: <b><i>{delta}%</i></b>",
                                 parse_mode="HTML")
            await state.clear()
        else:
            raise KeyError
    except ValueError:
        await message.answer("Введен неверный формат данных, повторите попытку.")
        return
    except KeyError:
        await message.answer("Количество вводимых данных должно "
                             "быть от 2 до 10. Повторите попытку")
        return


@user.message(Command(commands=['rec']))
async def start_rec(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("<b>Расчет объема вещества для приготовления раствора.</b>\n"
                         "Выберите вещество",
                         reply_markup=await kb_user.substance_kb(),
                         parse_mode="HTML")


@user.callback_query(F.data.startswith("substance"))
async def substance_callback(call: CallbackQuery, state: FSMContext):
    substance = call.data.split("_")[1]
    A, B, M = DENSITY[substance]["A"], DENSITY[substance]["B"], DENSITY[substance]["M"]
    await state.update_data(A=A, B=B, M=M, substance=substance)
    await call.message.answer(
        f"Вы выбрали {substance}.\n"
        f"Теперь введите значение плотности в пределах"
        f"от <u>1 до 1.2</u>(❗️)."
    )
    await state.set_state(st.SubstanceFSM.density)


@user.message(st.SubstanceFSM.density)
async def density_input(message: Message, state: FSMContext):
    try:
        density = float(message.text.replace(" ","").replace(",","").replace(",", "."))
        if density < 1 or density > 1.2:
            raise ValueError
        await state.update_data(density=density)
        await message.answer("Выберите объем колбы",
                             reply_markup=await kb_user.volumes_kb())
    except ValueError:
        await message.answer("Возникла ошибка по одной из причин:\n"
                             "- Введенное значение плотности находится за пределами диапазона 1-1.2;\n"
                             "- Некорректный формат значения плотности."
                             "Повторите ввод.")


@user.callback_query(F.data.startswith("volumes") and st.SubstanceFSM.density)
async def volumes_callback(call: CallbackQuery, state: FSMContext):
    try:
        volume = int(call.data.split("_")[1])
        data = await state.get_data()
        A, B, M = data["A"], data["B"], data["M"]
        density = data["density"]
        procent = A + B * density

        # Расчет исходной концентрации и объема
        c0 = (procent/100 * 1000 * density)/M
        await state.update_data(c0=c0, volume=volume)
        await call.message.answer("Введите требуемую концентрацию")
        await state.set_state(st.SubstanceFSM.finish)
    except Exception:
        await call.answer("Возникла ошибка, операция прервана")
        await state.clear()


@user.message(st.SubstanceFSM.finish)
async def substance_finish(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        substance, density = data["substance"], data["density"]
        c0, volume = data["c0"], data["volume"]
        c = float(message.text.replace(" ", ""). replace(",", "."))
        if c > c0:
            raise ValueError
        v0 = c * volume / c0
        pos_v0 = next(i for i, item in enumerate(str(v0)) if item != "0" and item != ".") + 1
        v0 = round(v0, pos_v0)
        await message.answer(f"Объем <i>{substance}</i> плотностью <i>{density}</i>, необходимый "
                             f"для приготовления раствора с концентрацией <i>{c}</i> в колбе <i>{volume} мл</i> "
                             f"составляет <b><i>{v0} мл</i></b>.",
                             parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("Концентрация разбавленного раствора не может "
                             "быть выше исходной концентрации.\n"
                             "Повторите ввод.")
        return
    except Exception:
        await message.answer("Некорретный формат. Повторите ввод")
        return

@user.message(Command(commands="test"))
async def test(message: Message):
    await db_reg.test_request()
    await message.answer("TEST")