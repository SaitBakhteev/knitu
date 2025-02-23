from aiogram.fsm.state import State, StatesGroup


class CreateAutoFSM(StatesGroup):
    user = State()
    brand = State()
    model = State()
    year = State()
    engine = State()
    mileage = State()
    image = State()


class CreateServiceFSM(StatesGroup):
    car_id=State()
    type=State()
    date=State()


class CarDeleteFSM(StatesGroup):
    car = State()
    user = State()


class CreateNotesFSM(StatesGroup):
    user = State()
    price = State()
    title = State()


class CreateRemindersFSM(StatesGroup):
    user = State()
    created_at = State()
    total_date = State()
    text = State()


class CreatePurchasesFSM(StatesGroup):
    id = State()
    text = State()
    price = State()
    image = State()


class CreateCategoryFSM(StatesGroup):
    title = State()
    animals = State()


class CreateQuestionFSM(StatesGroup):
    category = State()
    animal = State()
    text = State()
    answers = State()
    correct_answer = State()
    image = State()

class QuizFSM(StatesGroup):
    continue_quiz = State()