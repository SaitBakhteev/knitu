import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

DB_URL = os.getenv("DB_URL")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

STUDENT_CF = {
    "90": {
        "2": 6.3130,
        "3": 2.9200,
        "4": 2.35340,
        "5": 2.13180,
        "6": 2.01500,
        "7": 1.943,
        "8": 1.8946,
        "9": 1.8596,
        "10": 1.8331
    },
    "95": {
        "2": 12.7060,
        "3": 4.3020,
        "4": 3.182,
        "5": 2.776,
        "6": 2.570,
        "7": 2.4460,
        "8": 2.3646,
        "9": 2.3060,
        "10": 2.2622
    },
    "98": {
        "2": 31.820,
        "3": 6.964,
        "4": 4.540,
        "5": 3.746,
        "6": 3.649,
        "7": 3.1420,
        "8": 2.998,
        "9": 2.8965,
        "10": 2.8214
    },
    "99": {
        "2": 63.656,
        "3": 9.924,
        "4": 5.840,
        "5": 4.604,
        "6": 4.0321,
        "7": 3.7070,
        "8": 3.4995,
        "9": 3.3554,
        "10": 3.2498
    },
}

DEPARTMENT = [('ХТПНГ','HTPNG'),
              ('ТООНС','TOONS'),
              ('АХСМК','AHSMK'),
              ('ОХТ','OHT'),
              ('ТНВ','TNV'),]


'''Данные зависимости % от плотности. Коэффициенты линейной зависимости представлены
для диапазона плотностей 1-1.2'''

DENSITY = {
    "H2SO4": {"A": -129.46,
              "B": 130.74,
              "M": 98},

    "HCl": {"A": -198.04,
            "B": 198.54,
            "M": 36.5},

    "NaOH": {"A": -94.838,
            "B": 94.386,
            "M": 40}
}


TRAINING_TYPES = [('🏀', 'Баскетбол'),
                  ('⚽️', 'Футбол'),
                  ('🏐', 'Волейбол'),
                  ('🏒', 'Хоккей'),
                  ('🏸', 'Бадминтон'),
                  ('🏓', 'Настольный теннис')]


# config.py for MySQL

# TORTOISE_ORM = {
#     "connections": {
#         "default": {
#             "engine": "tortoise.backends.mysql",
#             "credentials": {
#                 "host": DB_HOST,
#                 "port": DB_PORT,
#                 "user": DB_USER,
#                 "password": DB_PASS,
#                 "database": DB_NAME,
#                 "minsize": 1,
#                 "maxsize": 5,
#                 "sql_mode": "STRICT_TRANS_TABLES"
#             },
#         }
#     },
#     "apps": {
#         "models": {
#             "models": ["app.database.models", "aerich.models"],
#             "default_connection": "default",
#         }
#     },
# }
#
#
# # postgres
# # TORTOISE_ORM = {
# #     "connections": {
# #         "default": {
# #             "engine": "tortoise.backends.asyncpg",
# #             "credentials": {
# #                 "host": DB_HOST,
# #                 "port": DB_PORT,
# #                 "user": DB_USER,
# #                 "password": DB_PASS,
# #                 "database": DB_NAME,
# #             },
# #         }
# #     },
# #     "apps": {
# #         "models": {
# #             "models": ["app.database.models", "aerich.models"],
# #             "default_connection": "default",
# #         }
# #     },
# # }
# #
# #
# #
# # # TYPE_CHOICES = [
# # #     ("OL", "OIL"),  # масло
# # #     ("FL", "filter"),  # фильтр
# # #     ("SP", "Support"),  # тормозные колодки
# # #     ("FS", "Full Service"),  # полное ТО
# # # ]
# #
# #
# # # # sqlite
TORTOISE_ORM = {
    "connections": {
        "default": DB_URL,
    },
    "apps": {
        "models": {
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
# #
# #
#
# #
