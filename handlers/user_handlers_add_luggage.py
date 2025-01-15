from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from services.zeep_soap import add_tickets
from config_data.config import Config, load_config
from keyboards.user_keyboard_order_ticket import keyboard_pay_ticket, keyboard_add_luggage
import logging


router = Router()
config: Config = load_config()


@router.callback_query(F.data == 'add_luggage')
async def add_luggage(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Оформление билета
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'add_luggage')
    data = await state.get_data()
    order_id = data['order_id']
    seat_num = data['seat_num']
    data_trip = data['data_trip']
    departure_time = data['departure_time']
    logging.info(f'add_luggage {order_id} {seat_num} {data_trip} {departure_time}')
    result = await add_tickets(order_id=order_id,
                               fare_name='Багажный',
                               seat_num=0,
                               parent_ticket_seat_num=seat_num)
    count_luggage = 0
    for fare in result["return"]['Tickets']:
        if fare['FareName'] == 'Багажный':
            count_luggage += 1
    await state.update_data(number=result['TicketSeats']['Elements'][0]['TicketNumber'])
    await callback.message.edit_text(text=f'Проверьте данные о маршруте:\n\n'
                                          f'<i>Отправление:</i> {result["return"]["Trip"]["Departure"]["Name"]}\n'
                                          f'<i>Прибытие:</i> {result["return"]["Trip"]["Destination"]["Name"]}\n'
                                          f'<i>Дата:</i> {data_trip}\n'
                                          f'<i>Время:</i> {departure_time.strftime("%H:%M")}\n'
                                          f'<i>Место:</i> {seat_num}\n'
                                          f'<i>Багаж:</i> {count_luggage}\n',
                                     reply_markup=keyboard_add_luggage())
    await callback.answer()

