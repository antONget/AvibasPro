from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import aiogram_calendar

from keyboards.user_keyboard_my_tickets import keyboards_my_tickets, keyboard_action_my_ticket
from database.requests import get_tickets_user, get_ticket_user_id_order, update_ticket, StatusTicket, \
    update_cancellation_details
from database.models import Tiket
from config_data.config import Config, load_config
from utils.error_handling import error_handler
from services.payments import refund_ticket
from services.zeep_soap import get_bus_stops, get_destinations, return_payment, add_ticket_return

from datetime import datetime
import logging

router = Router()
config: Config = load_config()


@router.message(F.text == 'Мои билеты')
@error_handler
async def press_button_my_tickets(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info('press_button_my_tickets')
    tickets: list[Tiket] = await get_tickets_user(tg_id=message.from_user.id)
    await message.answer(text=f'Выберите билет, который вы бы хотели вернуть или повторить заказ. '
                              f' 🔄 Разверните экран телефона для отображения полной информации',
                         reply_markup=keyboards_my_tickets(list_my_tickets=tickets))


@router.callback_query(F.data.startswith('my_ticket_'))
@error_handler
async def select_my_ticket(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info('select_my_ticket')
    answer = callback.data.split('_')[-1]
    ticket: Tiket = await get_ticket_user_id_order(id_order=answer)
    await callback.message.edit_text(text=f'Выберите действие для билета:\n'
                                          f'{ticket.departure_data} {ticket.departure_time} {ticket.departure} - {ticket.destination}',
                                     reply_markup=keyboard_action_my_ticket(id_order=answer))
    await callback.answer()


@router.callback_query(F.data.startswith('retry_my_order_'))
@error_handler
async def retry_my_order(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info('retry_my_order')
    answer = callback.data.split('_')[-1]
    ticket: Tiket = await get_ticket_user_id_order(id_order=answer)
    await state.update_data(departure=ticket.id_departure)
    await state.update_data(destination=ticket.id_destination)
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


@router.callback_query(F.data.startswith('refuse_my_ticket_'))
@error_handler
async def refuse_my_ticket(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Возврат билета
    :param callback: refuse_my_ticket_{id_order}
    :param state:
    :param bot:
    :return:
    """
    logging.info('refuse_my_ticket')
    id_order = callback.data.split('_')[-1]
    info_ticked = await get_ticket_user_id_order(id_order=id_order)
    amount = info_ticked.amount
    payment_id = info_ticked.payment_id
    refund = refund_ticket(amount=amount, payment_id=payment_id)
    if refund.status:
        ticket_return = await add_ticket_return(ticket_number=info_ticked.ticket_number,
                                                departure_id=info_ticked.id_departure,
                                                order_id=id_order)
        await return_payment(return_order_id=ticket_return['Number'],
                             terminal_id=0,
                             terminal_session_id=0,
                             payment_type='Other',
                             amount=amount)
        await callback.message.answer(text=f'Билет *{id_order}*:\n'
                                           f'{info_ticked.departure} - {info_ticked.destination}\n'
                                           f'{info_ticked.departure_data} {info_ticked.departure_time}\n'
                                           f'Успешно возвращен!')
        await update_ticket(id_order=id_order, status_payment=StatusTicket.refund)
    else:
        logging.info(f'refuse_my_ticket {refund.cancellation_details}')
        await update_cancellation_details(id_order=id_order, cancellation_details=str(refund.cancellation_details))
    await callback.answer()



