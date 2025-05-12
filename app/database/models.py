from tortoise.models import Model
from tortoise import fields


# поля с префиксом tg заполняются автоматически от телеграмм
class User(Model):
    id = fields.IntField(primary_key=True)
    tg_id = fields.BigIntField()
    tg_username = fields.CharField(max_length=100)
    tg_name = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_admin = fields.BooleanField(default=False)
    specialization = fields.ManyToManyField('models.Specialization',
                                            through='models.UserSpecialization',)
    full_name = fields.CharField(max_length=100)


class Specialization(Model):
    id = fields.IntField(primary_key=True)
    title = fields.TextField()  # название специальности
    department = fields.CharField(max_length=10)  # аббревиатура кафедры


class UserSpecialization(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField('models.User')
    specialization = fields.ForeignKeyField('models.Specialization')

    class Meta:
        # Защита от добавления повторной комбинации specialization, user
        unique_together = (('user', 'specialization'),)


class Question(Model):
    id = fields.IntField(primary_key=True)
    question = fields.TextField()
    answers = fields.JSONField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    specialization = fields.ForeignKeyField('models.Specialization')
    creator = fields.ForeignKeyField('models.User')
