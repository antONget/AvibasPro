from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext


from keyboards.user_keyboard_calendar import keyboards_trip
import aiogram_calendar
from datetime import datetime
from services.zeep_soap import get_trips
from config_data.config import Config, load_config
from utils.error_handling import error_handler
import logging

router = Router()
config: Config = load_config()


@router.callback_query(F.data.startswith('select_finish_station_'))
@error_handler
async def set_calendar(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выводим календарь для выбора даты поездки
    :param callback: select_finish_station_{station[-1]}
    station[-1] - Id автобусной остановки
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'set_calendar')
    await state.update_data(destination=callback.data.split('_')[-1])
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Выберите <b>ДАТУ ОТПРАВЛЕНИЯ</b>",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await callback.answer()


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter())
@error_handler
async def process_simple_calendar_start(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext,
                                        bot: Bot):
    """
    Обработка полученной даты поездки - вывод доступных рейсов
    :param callback:
    :param callback_data:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_simple_calendar_start {callback.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2030, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        data_trip = date.strftime("%Y-%m-%d")
        current_data = datetime.now()
        if (current_data - date).days > 0:
            await callback.answer(text='Некорректная дата', show_alert=True)
            calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
            calendar.set_dates_range(datetime(2024, 1, 1), datetime(2050, 12, 31))
            # получаем текущую дату
            current_date = datetime.now()
            # преобразуем ее в строку
            date1 = current_date.strftime('%d/%m/%Y')
            # преобразуем дату в список
            list_date1 = date1.split('/')
            await callback.message.edit_text(
                "Выберите <b>ДАТУ ОТПРАВЛЕНИЯ</b>",
                reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
            )
            return
        await state.update_data(data_trip=data_trip)
        data = await state.get_data()
        trips: dict = await get_trips(departure=data['departure'],
                                      destination=data['destination'],
                                      trips_date=data_trip)
        list_router = []
        for rout in trips['Elements']:
            if rout['DepartureTime'] > current_data:
                list_router.append([rout['Id'], rout['RouteNum'], rout['DepartureTime']])
        if list_router:
            await callback.message.edit_text(text='Выберите <b>РЕЙС</b>',
                                             reply_markup=keyboards_trip(list_routers=list_router))
        else:
            await callback.answer(text='Рейсов на выбранную дату нет', show_alert=True)
            calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
            calendar.set_dates_range(datetime(2024, 1, 1), datetime(2050, 12, 31))
            # получаем текущую дату
            current_date = datetime.now()
            # преобразуем ее в строку
            date1 = current_date.strftime('%d/%m/%Y')
            # преобразуем дату в список
            list_date1 = date1.split('/')
            await callback.message.edit_text(
                "Выберите <b>ДАТУ ОТПРАВЛЕНИЯ</b>",
                reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
            )
            return
    await callback.answer()
