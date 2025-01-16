from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time, timedelta, datetime
import logging


def keyboards_trip(list_routers: list):
    """
    Клавиатура для вывода рейсов
    :param list_routers:
    :return:
    """
    logging.info(f"keyboards_slots")
    # [rout['Id'], rout['RouteNum'], rout['DepartureTime']
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for rout in list_routers:
        data_trip = rout[2].strftime("%H:%M")
        text = f'№ {rout[1]} - {data_trip}'
        callback = f'router_{rout[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=callback))
    kb_builder.row(*buttons, width=1)
    back = [InlineKeyboardButton(
        text='Назад',
        callback_data='back_dialog_calendar')]
    kb_builder.row(*back, width=1)
    return kb_builder.as_markup()
