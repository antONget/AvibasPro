from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.user_keyboard_calendar import keyboards_trip
import aiogram_calendar
from datetime import datetime
from services.zeep_soap import get_trips, get_trips_segment
from config_data.config import Config, load_config
import logging

router = Router()
config: Config = load_config()


class Calendar(StatesGroup):
    start = State()
    feedbak = State()


@router.callback_query(F.data.startswith('select_finish_station_'))
async def set_calendar(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подключаем календарь
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'set_calendar')
    await state.update_data(destination=callback.data.split('_')[-1])
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
    await state.set_state(Calendar.start)
    await callback.answer()


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Calendar.start))
async def process_simple_calendar_start(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    logging.info(f'process_simple_calendar_start {callback.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date = await calendar.process_selection(callback, callback_data)
    if selected:
        data_trip = date.strftime("%Y-%m-%d")
        await state.update_data(data_trip=data_trip)
        data = await state.get_data()
        trips: dict = await get_trips(departure=data['departure'], destination=data['destination'], trips_date=data_trip)
        list_router = []
        for rout in trips['Elements']:
            list_router.append([rout['Id'], rout['RouteNum'], rout['DepartureTime']])
        await callback.message.edit_text(text='Выберите <b>РЕЙС</b>',
                                         reply_markup=keyboards_trip(list_routers=list_router))
    await callback.answer()


