import asyncio
import random

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter, or_f

from database import requests as rq
from keyboards import user_keyboard_select_station as kb
from utils.error_handling import error_handler
from services.zeep_soap import get_bus_stops, get_destinations

import logging

router = Router()
router.message.filter(F.chat.type == "private")


# Определение состояний
class ButtonBack(StatesGroup):
    back_departure = State()
    back_destination = State()


@router.message(CommandStart())
@router.message(F.text == '🏠 Главное меню')
@error_handler
async def process_press_start(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработка команды /start
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_press_start')
    await state.set_state(state=None)
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = 'USER'
    data_user = {'tg_id': message.from_user.id, 'username': username}
    await rq.add_user(data=data_user)
    await message.answer(text=f'Добро пожаловать в бота по продаже билетов на автобусы пригородного сообщения.'
                              f' Здесь вы можете быстро и удобно приобрести билеты на любой маршрут,'
                              f' выбрав удобное время и место отправления.',
                         reply_markup=kb.keyboard_main_button())


@router.message(F.text == 'Купить билет')
@error_handler
async def press_button_pay_ticket(message: Message, bot: Bot, state: FSMContext):
    """
    Запуск процедуры покупки билета
    :param message:
    :param bot:
    :param state:
    :return:
    """
    logging.info('press_button_pay_ticket')
    await message.answer(text='В этом разделе вы можете выбрать направление, рейс и дату поездки, оформить билет',
                         reply_markup=kb.keyboard_major_button())
    await message.answer(text='Выберите пункт отправления',
                         reply_markup=kb.keyboards_select_start_station())


@router.callback_query(F.data == 'select_start_station_other')
@error_handler
async def select_start_station_other(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор станции отправления (стартовое меню)
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_start_station_other')
    await state.set_state(ButtonBack.back_departure)
    dict_get_bus_stops: list[dict] = await get_bus_stops()
    await callback.message.edit_text(text='Выберите с какой буквы(букв) начинается название <b>ПУНКТА ОТПРАВЛЕНИЯ</b>',
                                     reply_markup=
                                     kb.keyboards_select_first_word_station(dict_get_bus_stops=dict_get_bus_stops,
                                                                            count_letter=1))
    await callback.answer()


@router.callback_query(F.data.startswith('select_start_station_letter_'))
@error_handler
async def select_start_station_first_letter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор станции отправления по буквам
    :param callback: select_start_station_letter_{count_letter}_{first_letter[:count_letter]}
    count_letter - количество первых букв для вывода на клавиатуру
    first_letter[:count_letter] - набор букв с которого начинается стация отправления
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_start_station_first_letter')
    dict_get_bus_stops: list[dict] = await get_bus_stops()
    count_letter = int(callback.data.split('_')[-2]) + 1
    first_letter = callback.data.split('_')[-1]
    await callback.message.edit_text(text='Выберите с какой буквы(букв) начинается название <b>ПУНКТА ОТПРАВЛЕНИЯ</b>',
                                     reply_markup=
                                     kb.keyboards_select_first_word_station(dict_get_bus_stops=dict_get_bus_stops,
                                                                            count_letter=count_letter,
                                                                            letter=first_letter))
    await callback.answer()


@router.callback_query(F.data.startswith('select_start_station_'))
@error_handler
async def select_finish_station(callback: CallbackQuery, state: FSMContext, bot: Bot, press_button_back: bool = False):
    """
    Выбор станции отправления по названию.
    :param callback: select_start_station_{station[-1]}
    {station[-1]} - Id автобусной остановки
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_finish_station')
    await state.set_state(ButtonBack.back_departure)
    if press_button_back:
        data = await state.get_data()
        departure = data["departure"]
    else:
        departure: str = callback.data.split('_')[-1]
        await state.update_data(departure=departure)
    dict_get_bus_stops: list[dict] = await get_destinations(departure=departure)
    await callback.message.edit_text(text='Выберите с какой буквы(букв) начинается название <b>ПУНКТА НАЗНАЧЕНИЯ</b>',
                                     reply_markup=
                                     kb.keyboards_select_first_word_station_finish(dict_get_bus_stops=dict_get_bus_stops,
                                                                                   count_letter=1))
    await callback.answer()


@router.callback_query(F.data.startswith('select_finish_station_letter_'))
@error_handler
async def select_finish_station_letter(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор станции назначения по буквам
    :param callback: select_finish_station_letter_{count_letter}_{first_letter[:count_letter]}
    count_letter - количество первых букв для вывода на клавиатуру
    first_letter[:count_letter] - набор букв с которого начинается стация назначения
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_finish_station_letter')
    await state.set_state(ButtonBack.back_destination)
    data: dict = await state.get_data()
    dict_get_bus_stops: list[dict] = await get_destinations(departure=data['departure'])
    count_letter: int = int(callback.data.split('_')[-2]) + 1
    first_letter: str = callback.data.split('_')[-1]
    await callback.message.edit_text(text='Выберите с какой буквы(букв) начинается название <b>ПУНКТА НАЗНАЧЕНИЯ</b>',
                                     reply_markup=
                                     kb.keyboards_select_first_word_station_finish(dict_get_bus_stops=dict_get_bus_stops,
                                                                                   count_letter=count_letter,
                                                                                   letter=first_letter))
    await callback.answer()


@router.callback_query(F.data == 'back_dialog')
@error_handler
async def back_dialog(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('back_dialog')
    current_state = (await state.get_state()).split(':')[-1]
    if current_state == 'back_departure':
        await callback.message.edit_text(text='Выберите пункт отправления',
                                         reply_markup=kb.keyboards_select_start_station())
    elif current_state == 'back_destination':
        await select_finish_station(callback=callback, state=state, bot=bot, press_button_back=True)
