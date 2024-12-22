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
    logging.info(f"keyboards_trip")
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
    return kb_builder.as_markup()


seats_scheme_default = [[1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 1, 1]]


def keyboards_seat(seats_scheme: list[dict] = None, seats_reserved: list[dict] = None, show_row: int = 4, block: int = 0):
    """
    Клавиатура для вывода места
    :param seats_scheme:
    [
        {
            'XPos': 14,
            'YPos': 5,
            'SeatNum': 49,
            'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
        }
    ]
    :param seats_reserved:
    [
        {
            'Type': 'Passenger',
            'Number': 1,
            'Status': 'Reserved',
            'ParentTicketSeatNum': 0,
            'ForCurrentOrder': False
        }
    ]
    :param show_row:
    :param block:
    :return:
    """
    logging.info(f"keyboards_seat")
    seats_scheme_ = []
    if not seats_scheme:
        seats_scheme_ = seats_scheme_default
    else:
        i = 1  # инициализация счетчика рядов в схеме посадки
        row = []  # список возможности приобрести билет на место в ряду
        # формируем массив посадки
        for seat_row in seats_scheme:
            # формируем ряд посадки
            if seat_row['XPos'] == i:
                if seat_row['YPos'] == 6:
                    continue
                # если место определено
                if seat_row['SeatNum']:
                    row.append(seat_row['SeatNum'])
                else:
                    row.append(0)
            # формируем новый ряд
            else:
                i += 1
                seats_scheme_.append(row)
                row = []
                # если место определено
                if seat_row['SeatNum']:
                    row.append(seat_row['SeatNum'])
                else:
                    row.append(0)
        # добавляем последний ряд если он не пустой
        if row:
            seats_scheme_.append(row)
        # формируем массив резерва
        list_reserved = []
        # print("SEAT_RESERVED", seats_reserved, sep='\n')
        for reserved_item in seats_reserved:
            list_reserved.append(reserved_item['Number'])
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    row = 0
    # print("LIST_RESERVED", list_reserved, sep='\n')
    # формирование клавиатуры выбора мест
    for seats in seats_scheme_[show_row*block:show_row*(block+1)]:
        # формируем по рядам
        row += 1
        # [3, 4, 0, 2, 1]
        for item in seats:
            # если место в позиции определено и не занято - 🟩, если занято - 🟥, если не определено - ⬜️
            if item:
                if item not in list_reserved:
                    text = f'{item} 🟩'
                    callback = f'select_seat_{item}'
                else:
                    text = f'{item} 🟥'
                    callback = f'select_seat_busy'
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback))
            else:
                text = '⬜'
                callback = f'select_seat_default'
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback))
    kb_builder.row(*buttons, width=len(seats_scheme_[0]))
    # блок кнопок для переключения между рядами
    seat_block = []
    temp1 = 0
    temp2 = 0
    # если количество рядов в схеме больше чем отображаем на клавиатуре
    if len(seats_scheme_) > show_row:
        # # получаем количество отображаемых кнопок
        # count_block = len(seats_scheme_) // show_row
        i = -1
        for row1, row2 in zip(seats_scheme_[::show_row], seats_scheme_[show_row-1::show_row]):
            i += 1
            temp1 = sorted(row1)[1]
            temp2 = max(row2)
            text = f'{temp1} - {temp2}'
            callback = f'select_count_block_{i}'
            seat_block.append(InlineKeyboardButton(text=text, callback_data=callback))
        if len(seats_scheme_) % show_row:
            count_block = len(seats_scheme_) // show_row
            temp1 = sorted(seats_scheme_[count_block*show_row])[1]
            temp2 = max(seats_scheme_[-1])
            text = f'{temp1} - {temp2}'
            callback = f'select_count_block_{i+1}'
            seat_block.append(InlineKeyboardButton(text=text, callback_data=callback))
    kb_builder.row(*seat_block, width=2)
    return kb_builder.as_markup()


def keyboard_confirm() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Оформить билет', callback_data='confirm')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_pay_ticket() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Купить билет', callback_data='pay_ticket')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard
