from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from services.zeep_soap import add_tickets
from config_data.config import Config, load_config
from keyboards.user_keyboard_order_ticket import keyboard_pay_ticket
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
    result = await add_tickets(order_id=order_id,
                               fare_name='Багажный',
                               seat_num=0,
                               parent_ticket_seat_num=seat_num)
    await state.update_data(number=result['TicketSeats']['Elements'][0]['TicketNumber'])
    await callback.message.edit_text(text='Данные успешно добавлены',
                                     reply_markup=keyboard_pay_ticket())
    await callback.answer()

