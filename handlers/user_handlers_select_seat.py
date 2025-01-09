from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.user_keyboard_select_seat import keyboards_seat, keyboard_confirm
from services.zeep_soap import get_trips_segment, get_occupied_seats, start_sale_session
from config_data.config import Config, load_config
from utils.error_handling import error_handler
import logging

router = Router()
config: Config = load_config()


@router.callback_query(F.data.startswith('router_'))
@error_handler
async def select_num_router(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор свободного места на выбранный рейс
    :param callback: router_{rout[0]}
    rout[0] - id рейса
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'select_num_router')
    trip_id = callback.data.split('_')[-1]
    data = await state.get_data()
    occupied_seats = await get_occupied_seats(trip_id=trip_id,
                                              departure=data['departure'],
                                              destination=data['destination'],
                                              order_id=trip_id)
    trips_segment = await get_trips_segment(trip_id=trip_id,
                                            departure=data['departure'],
                                            destination=data['destination'])
    await state.update_data(departure_time=trips_segment['DepartureTime'])
    await state.update_data(trip_id=trip_id)
    dict_bus = occupied_seats['Bus']
    dict_seats_scheme = dict_bus['SeatsScheme']
    if occupied_seats['return']:
        dict_reserved = occupied_seats['return']['Elements']
    else:
        dict_reserved = {}
    await callback.message.edit_text(text=f'Выберите свободное <b>МЕСТО</b>',
                                     reply_markup=keyboards_seat(seats_scheme=dict_seats_scheme,
                                                                 seats_reserved=dict_reserved))
    await callback.answer()


@router.callback_query(F.data.startswith('select_count_block_'))
@error_handler
async def select_count_block(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор свободного места на выбранный рейс - переключение по блокам рядов в автобусе
    :param callback: select_count_block_{i+1}
    {i+1} - номер блока для выбора мест в автобусе
    :param state:
    :param bot:
    :return:
    """
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
    try:
        await callback.message.edit_text(text=f'Выберите свободное <b>МЕСТО</b>',
                                         reply_markup=keyboards_seat(seats_scheme=dict_seats_scheme,
                                                                     block=block,
                                                                     seats_reserved=dict_reserved))
    except:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith('select_seat_'))
@error_handler
async def select_seat_num(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обработка выбранного места
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_seat_num')
    seat: str = callback.data.split('_')[-1]
    if seat == 'default':
        await callback.answer()
    elif seat == 'busy':
        await callback.answer(text='Это место уже занято, выберите другое место', show_alert=True)
    else:
        seat_num: int = int(seat)
        await state.update_data(seat_num=seat_num)
        data = await state.get_data()
        data_trip = data['data_trip']
        departure_time = data['departure_time']
        print('trip_id', data['trip_id'], 'departure', data['departure'], 'destination', data['destination'], 'order_id', '')
        sale_session = await start_sale_session(trip_id=data['trip_id'],
                                                departure=data['departure'],
                                                destination=data['destination'],
                                                order_id='')
        await state.update_data(order_id=sale_session['Number'])
        await callback.message.edit_text(text=f'Проверьте данные о маршруте:\n\n'
                                              f'<i>Отправление:</i> {sale_session["Departure"]["Name"]}\n'
                                              f'<i>Прибытие:</i> {sale_session["Destination"]["Name"]}\n'
                                              f'<i>Дата:</i> {data_trip}\n'
                                              f'<i>Время:</i> {departure_time.strftime("%H:%M")}\n'
                                              f'<i>Место:</i> {seat_num}\n',
                                         reply_markup=keyboard_confirm())
        await callback.answer()
