from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.user_keyboard_select_seat import keyboards_seat, keyboard_confirm
import aiogram_calendar
from datetime import datetime
from services.zeep_soap import get_trips, get_trips_segment, get_occupied_seats, start_sale_session
from config_data.config import Config, load_config
import logging

router = Router()
config: Config = load_config()


class Calendar(StatesGroup):
    start = State()
    feedbak = State()


@router.callback_query(F.data.startswith('router_'))
async def set_calendar(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подключаем календарь
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'set_calendar')
    Id = callback.data.split('_')[-1]
    data = await state.get_data()
    occupied_seats = await get_occupied_seats(trip_id=Id,
                                              departure=data['departure'],
                                              destination=data['destination'],
                                              order_id=Id)
    # print('-1-', occupied_seats)
    # print('-2-', sale_session)
    trips_segment = await get_trips_segment(trip_id=Id,
                                            departure=data['departure'],
                                            destination=data['destination'])
    await state.update_data(departure_time=trips_segment['DepartureTime'])
    await state.update_data(trip_id=Id)
    dict_bus = occupied_seats['Bus']
    dict_seats_scheme = dict_bus['SeatsScheme']
    if occupied_seats['return']:
        dict_reserved = occupied_seats['return']['Elements']
    else:
        dict_reserved = {}
    await callback.message.answer(text=f'Выберите свободное место {dict_bus["SeatCapacity"]}',
                                  reply_markup=keyboards_seat(seats_scheme=dict_seats_scheme,
                                                              seats_reserved=dict_reserved))


@router.callback_query(F.data.startswith('select_count_block_'))
async def select_count_block(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('select_count_block')
    block = int(callback.data.split('_')[-1])
    data = await state.get_data()
    trips_segment = await get_trips_segment(trip_id=data['trip_id'],
                                            departure=data['departure'],
                                            destination=data['destination'])
    dict_bus = trips_segment['Bus']
    dict_seats_scheme = dict_bus['SeatsScheme']
    occupied_seats = await get_occupied_seats(trip_id=data['trip_id'],
                                              departure=data['departure'],
                                              destination=data['destination'],
                                              order_id=data['trip_id'])
    if occupied_seats['return']:
        dict_reserved = occupied_seats['return']['Elements']
    else:
        dict_reserved = {}
    await callback.message.answer(text=f'Выберите свободное место',
                                  reply_markup=keyboards_seat(seats_scheme=dict_seats_scheme,
                                                              block=block,
                                                              seats_reserved=dict_reserved))


@router.callback_query(F.data.startswith('select_seat_'))
async def select_seat_(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('select_seat_')
    seat: str = callback.data.split('_')[-1]
    if seat == 'default':
        await callback.answer()
    elif seat == 'busy':
        await callback.answer(text='Это место уже занято, выберите другое место', show_alert=True)
    else:
        seat_num: int = int(seat)
        await state.update_data(seat_num=seat_num)
        data = await state.get_data()
        id_departure = data['departure']
        id_destination = data['destination']
        data_trip = data['data_trip']
        departure_time = data['departure_time']
        sale_session = await start_sale_session(trip_id=data['trip_id'],
                                                departure=data['departure'],
                                                destination=data['destination'],
                                                order_id='')
        await state.update_data(order_id=sale_session['Number'])
        await callback.message.answer(text=f'Проверьте данные о маршруте:\n\n'
                                           f'<i>Отправление:</i> {sale_session["Departure"]["Name"]}\n'
                                           f'<i>Прибытие:</i> {sale_session["Destination"]["Name"]}\n'
                                           f'<i>Дата:</i> {data_trip}\n'
                                           f'<i>Время:</i> {departure_time}\n'
                                           f'<i>Место:</i> {seat_num}\n',
                                      reply_markup=keyboard_confirm())

