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


