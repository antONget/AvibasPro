import asyncio
import random

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
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
class User(StatesGroup):
    description = State()
    photo = State()
    info = State()
    cost = State()


@router.message(CommandStart())
@error_handler
async def process_press_start(message: Message, state: FSMContext, bot: Bot) -> None:
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
    logging.info('press_button_pay_ticket')
    await message.answer(text='Выберите пункт отправления',
                         reply_markup=kb.keyboards_select_start_station())


@router.callback_query(F.data == 'select_start_station_other')
@error_handler
async def select_start_station_other(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('select_start_station_other')
    dict_get_bus_stops: list[dict] = await get_bus_stops()
    await callback.message.edit_text(text='Выберите с какой буквы(букв) начинается название <b>ПУНКТА ОТПРАВЛЕНИЯ</b>',
                                     reply_markup=
                                     kb.keyboards_select_first_word_station(dict_get_bus_stops=dict_get_bus_stops,
                                                                            count_letter=1))
    await callback.answer()


@router.callback_query(F.data.startswith('select_start_station_letter_'))
@error_handler
async def select_start_station_first_letter(callback: CallbackQuery, state: FSMContext, bot: Bot):
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
async def select_finish_station(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('select_finish_station')
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
    logging.info('select_finish_station_letter')
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
