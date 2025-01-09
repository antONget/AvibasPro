from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Tiket
import logging


def keyboards_my_tickets(list_my_tickets: list[Tiket]) -> InlineKeyboardMarkup:
    logging.info(f"keyboards_my_tickets")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for ticket in list_my_tickets:
        text_button = f"{ticket.departure_data} {ticket.departure_time} {ticket.departure}-{ticket.destination}"
        callback_button = f'my_ticket_{ticket.id_order}'
        buttons.append(InlineKeyboardButton(
            text=text_button,
            callback_data=callback_button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_action_my_ticket(id_order: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Повторить заказ', callback_data=f'retry_my_order_{id_order}')
    button_2 = InlineKeyboardButton(text='Вернуть билет', callback_data=f'refuse_my_ticket_{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard
