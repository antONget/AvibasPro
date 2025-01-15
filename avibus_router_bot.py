from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import Config, load_config
from handlers import user_handlers_select_station,\
                     user_handlers_select_datetime, \
                     user_handlers_select_seat, \
                     user_handlers_order_ticket, \
                     user_handlers_add_luggage, \
                     user_handlers_my_tickets, \
                     other_handlers

from notify_admins import on_startup_notify
from database.models import async_main
import asyncio
import logging
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    await async_main()
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        # filename="py_log.log",
        # filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # storage = RedisStorage.from_url('redis://127.0.0.1:6379/6')
    dp = Dispatcher()
    await on_startup_notify(bot=bot)
    # Регистрируем router в диспетчере
    dp.include_router(user_handlers_select_station.router)
    dp.include_router(user_handlers_select_datetime.router)
    dp.include_router(user_handlers_select_seat.router)
    dp.include_router(user_handlers_order_ticket.router)
    dp.include_router(user_handlers_add_luggage.router)
    dp.include_router(user_handlers_my_tickets.router)
    dp.include_router(other_handlers.router)



    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
