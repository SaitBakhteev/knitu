"""  Базу данных, являющиеся основой работы приложения, составляют следующие модели:
    1. Модель User. При этом в этой модели поле "admin_permissions" определяет, обладает ли пользователь правами
        админа. Админу доступна панель кнопок вида ReplyKeyboardMarkup, с помощью которой можно добавлять в БД объекты
        модели Question и Category (возможно будет добалена возможность редактирования и удаления). Помимо этого, стоит
        отметить, что поле "totemic_animal" содержит название тотемного животного по результатам последнего опроса.
    2. Questions - это вопросы с вариантами ответов. Варианты ответов, в поле "answers", представляющее собой
        список словарей с ключами "answer" и "is_correct_answer", а правильный ответ имеет значение
        ключа "is_correct_answer"
    3. Category - это модель, позволяющая группировать вопросы по разным категориям. В текущем функционале для
        имеющихся задач программы данная модель особо пользы пока не несёт, но возможно она окажется полезна для
        расширения в будущем функционала программы и некоторых задач для администрирования программы.
        Примеры категорий вопросов: "Животные Индии", "Жвачные парнокопытные", "Животные тундры" и т.п.
        Поле keywords позволяет хранить ключевые слова, которые сопоставляются с ответами пользователя.
        Данное поле актуально, когда вопрос из категории не о животных, а о пользователе. Значения keywords
        позволяют дополнительно определить тотемное животное
    4. Survey - это модель, содержащая записи результатов опроса-викторины.

Дополнительная модель DeletedObjects хранит id удаленных объектов вышеприведенных моделей,
значения которых находятся в промежутке между id=1   из БД    """


from tortoise.models import Model
from tortoise import fields


# поля с префиксом tg заполняются автоматически от телеграмм
class User(Model):
    id = fields.IntField(primary_key=True)
    tg_id = fields.BigIntField()
    tg_username = fields.CharField(max_length=100)
    tg_name = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    admin_permissions = fields.BooleanField(default=False)
    totemic_animal = fields.CharField(max_length=20, null=True)


class Category(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=50)

    ''' Здесь должен быть список животных. Но если это вопрос
    про пользователя то это поле пусто '''
    animals = fields.JSONField(null=True)



    def __str__(self):
        return self.title


class Question(Model):
    id = fields.IntField(primary_key=True)
    text = fields.TextField()
    answers = fields.JSONField(null=True)

    # название категории вопроса
    category = fields.ForeignKeyField("models.Category", related_name='question')

    # Путь на файл для загрузки изображения животного, когда про него звучит вопрос
    image_path = fields.TextField()

    # название животного из словаря ANIMALS, про которого звучит вопрос
    animal = fields.CharField(max_length=50)

    def __str__(self):
        return self.text[:10]


# Результаты опроса-викторины
class Survey(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name='survey')
    survey_date = fields.DatetimeField(auto_now_add=True)

    # Результат опроса в виде текста. Пример:
    # "Набрано 45 баллов из 68. Тотемное животное-Бенгальский тигр"
    result = fields.CharField(max_length=50)


