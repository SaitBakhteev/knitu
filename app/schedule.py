from datetime import datetime, timedelta

from app.database.models import User, Category, Question, Answer, Survey
#
#
# async def check_service_reminders():
#     from run import bot
#
#     now = datetime.now().date()
#
#     # services_due = await Service.filter(next_service_date__lte=now).prefetch_related(
#     #     "car"
#     # )
#
#     # for service in services_due:
#     #     user_id = service.car.user.tg_id
#     #
#     #     message_text = f"Напоминание: следующий {service.type} для вашего автомобиля {service.car.model} запланирован на {service.next_service_date}."
#     #
#     #     await bot.send_message(user_id, message_text)
#     #
#     #     service.next_service_date = service.next_service_date + timedelta(days=240)
#     #     await service.save()
#
#
# async def check_reminders():
#     from run import bot
#
#     now = datetime.now()
#
#     reminders = await Reminders.filter(total_date__lte=now).prefetch_related("user")
#
#     for reminder in reminders:
#         await bot.send_message(reminder.user.tg_id, reminder.text)
#
#         await reminder.delete()
#
#
# async def send_seasonal_notifications():
#     from run import bot
#
#     users = await User.all()
#     for user in users:
#         await bot.send_message(user.tg_id, "Время поменять омывайку и шины")