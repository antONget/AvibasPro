from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_main_button() -> ReplyKeyboardMarkup:
    logging.info('keyboard_main_button')
    button_1 = KeyboardButton(text='Мои билеты')
    button_2 = KeyboardButton(text='Купить билет')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_major_button() -> ReplyKeyboardMarkup:
    logging.info('keyboard_major_button')
    button_1 = KeyboardButton(text='🏠 Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard


def keyboards_select_start_station() -> InlineKeyboardMarkup:
    logging.info(f"keyboards_select_start_station")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    main_stations = [['Лодейное Поле', '6d9b1c62-e61f-11ee-81e3-d00d4cbcd401'],
                     ['Санкт-Петербург', '80979b40-5d41-11ee-8668-d00d4cbcd401'],
                     ['Подпорожье', 'e3223f2e-e61f-11ee-81e3-d00d4cbcd401'],
                     ['Тихвин', 'be1cc470-e52e-11ee-92d2-d00d4cbcd401'],
                     ['Пикалёво', 'e3ef2522-e5f0-11ee-9959-d00d4cbcd401'],
                     ['Сясьстрой', '26db9652-e5e4-11ee-94e0-d00d4cbcd401']]
    for station in main_stations:
        text = f'{station[0]}'
        button = f'select_start_station_{station[1]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_other_station = InlineKeyboardButton(text='Другая',
                                                callback_data=f'select_start_station_other')
    kb_builder.row(*buttons, width=2)
    kb_builder.row(button_other_station)
    return kb_builder.as_markup()


def keyboards_select_first_word_station(dict_get_bus_stops: list[dict], count_letter: int, letter: str = '')\
        -> InlineKeyboardMarkup:
    logging.info(f"keyboards_select_first_word_station {count_letter} {letter}")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    temp_buttons_letter = []
    temp_station = []
    for station in dict_get_bus_stops:
        if letter:
            if station["Name"].startswith(letter):
                if f'{station["Name"][0:count_letter]}' not in temp_buttons_letter:
                    temp_buttons_letter.append(f'{station["Name"][0:count_letter]}')
                if [station["Name"], station["Id"]] not in temp_station:
                    temp_station.append([station["Name"], station["Id"]])
        else:
            if f'{station["Name"][0:count_letter]}' not in temp_buttons_letter:
                temp_buttons_letter.append(f'{station["Name"][0:count_letter]}')
            if [station["Name"], station["Id"]] not in temp_station:
                temp_station.append([station["Name"], station["Id"]])
    if len(temp_station) < 5:
        temp_station.sort(reverse=False)
        for station in temp_station:
            text = station[0]
            callback = f'select_start_station_{station[-1]}'
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=callback))
        kb_builder.row(*buttons, width=1)
    else:
        temp_buttons_letter.sort(reverse=False)
        for first_letter in temp_buttons_letter:
            text = first_letter
            callback = f'select_start_station_letter_{count_letter}_{first_letter[:count_letter]}'
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=callback))
        kb_builder.row(*buttons, width=3)
    back = [InlineKeyboardButton(
        text='Назад',
        callback_data='back_dialog')]
    kb_builder.row(*back, width=1)
    return kb_builder.as_markup()


def keyboards_select_finish_station() -> InlineKeyboardMarkup:
    logging.info(f"keyboards_select_start_station")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    main_stations = [['Лодейное Поле', '6d9b1c62-e61f-11ee-81e3-d00d4cbcd401'],
                     ['Санкт-Петербург', '80979b40-5d41-11ee-8668-d00d4cbcd401'],
                     ['Подпорожье', 'e3223f2e-e61f-11ee-81e3-d00d4cbcd401'],
                     ['Тихвин', 'be1cc470-e52e-11ee-92d2-d00d4cbcd401'],
                     ['Пикалёво', 'e3ef2522-e5f0-11ee-9959-d00d4cbcd401'],
                     ['Сясьстрой', '26db9652-e5e4-11ee-94e0-d00d4cbcd401']]
    for station in main_stations:
        text = f'{station[0]}'
        button = f'select_finish_station_{station[1]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_other_station = InlineKeyboardButton(text='Другая',
                                                callback_data=f'select_finish_station_other')
    kb_builder.row(*buttons, width=2)
    kb_builder.row(button_other_station)
    return kb_builder.as_markup()


def keyboards_select_first_word_station_finish(dict_get_bus_stops: list[dict], count_letter: int, letter: str = '')\
        -> InlineKeyboardMarkup:
    logging.info(f"keyboards_select_first_word_station_finish {count_letter} {letter}")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    temp_buttons_letter = []
    temp_station = []
    for station in dict_get_bus_stops:
        if letter:
            if station["Name"].startswith(letter):
                if f'{station["Name"][0:count_letter]}' not in temp_buttons_letter:
                    temp_buttons_letter.append(f'{station["Name"][0:count_letter]}')
                if [station["Name"], station["Id"]] not in temp_station:
                    temp_station.append([station["Name"], station["Id"]])
        else:
            if f'{station["Name"][0:count_letter]}' not in temp_buttons_letter:
                temp_buttons_letter.append(f'{station["Name"][0:count_letter]}')
            if [station["Name"], station["Id"]] not in temp_station:
                temp_station.append([station["Name"], station["Id"]])
    if len(temp_station) < 5:
        temp_station.sort(reverse=False)
        for station in temp_station:
            text = station[0]
            callback = f'select_finish_station_{station[-1]}'
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=callback))
        kb_builder.row(*buttons, width=1)
    else:
        temp_buttons_letter.sort(reverse=False)
        for first_letter in temp_buttons_letter:
            text = first_letter
            callback = f'select_finish_station_letter_{count_letter}_{first_letter[:count_letter]}'
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=callback))
        kb_builder.row(*buttons, width=3)
    back = [InlineKeyboardButton(
        text='Назад',
        callback_data='back_dialog')]
    kb_builder.row(*back, width=1)
    return kb_builder.as_markup()
