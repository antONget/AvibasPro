from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.user_keyboard_order_ticket import keyboard_pay_ticket, keyboard_gender, keyboard_citizenship
import aiogram_calendar
from datetime import datetime
from services.zeep_soap import add_tickets, set_ticket_data, reserve_order, payment_ticket
from config_data.config import Config, load_config
import logging
import re

router = Router()
config: Config = load_config()


class Order_ticket(StatesGroup):
    data_personal = State()
    data_passport = State()
    data_birthday = State()
    citizenship = State()


@router.callback_query(F.data == 'confirm')
async def order_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Оформление билета
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'order_ticket')
    data = await state.get_data()
    order_id = data['order_id']
    seat_num = data['seat_num']
    result = await add_tickets(order_id=order_id,
                               fare_name='Пассажирский',
                               seat_num=seat_num,
                               parent_ticket_seat_num=0)
    await state.update_data(number=result['TicketSeats']['Elements'][0]['TicketNumber'])
    await callback.message.answer(text='Пришлите Ваши ФИО (например: Иванов Сергей Игоревич)')
    await state.set_state(state=Order_ticket.data_personal)


@router.message(F.text, StateFilter(Order_ticket.data_personal))
async def get_data_personal(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_data_personal')
    name_pattern = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$')
    if name_pattern.match(message.text):
        await state.update_data(name=message.text)
        await message.answer(text='Укажите ваш пол',
                             reply_markup=keyboard_gender())
        await state.set_state(Order_ticket.data_passport)
    else:
        await message.answer(text='Некорректные введенные данные, пришлите ФИО в формате: Иванов Сергей Игоревич')


@router.callback_query(F.data.startswith("gender_"))
async def get_data_gender(calback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('get_data_gender')
    answer = calback.data.split('_')[-1]
    if answer == 'male':
        await state.update_data(gender='Мужской')
    else:
        await state.update_data(gender='Женский')
    await calback.message.answer(text='Пришлите паспортные данные (например: 12 34 123456')
    await state.set_state(Order_ticket.data_passport)


@router.message(F.text, StateFilter(Order_ticket.data_passport))
async def get_data_pasport(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_data_pasport')
    name_pattern = re.compile(r'\b[0-9]{2}\s?[0-9]{2}\s?[0-9]{6}\b')
    if name_pattern.match(message.text):
        await state.update_data(document_number=message.text)
        await message.answer(text='Укажите дату вашего рождения, в формате: дд-мм-гггг')
        await state.set_state(Order_ticket.data_birthday)
    else:
        await message.answer(text='Некорректные введенные данные, пришлите данные в формате: 12 34 123456')


@router.message(F.text, StateFilter(Order_ticket.data_birthday))
async def get_data_birthday(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_data_pasport')
    birthday_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b')
    if birthday_pattern.match(message.text):
        await state.update_data(birthday=message.text)
        await message.answer(text='Укажите ваше гражданство',
                             reply_markup=keyboard_citizenship())
        await state.set_state(Order_ticket.citizenship)
    else:
        await message.answer(text='Некорректные введенные данные, пришлите данные в формате: дд-мм-гггг')


@router.callback_query(F.data == 'citizenship_RUSSIA')
async def get_citizenship(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'get_citizenship')
    await state.set_state(state=None)
    await state.update_data(citizenship='РОССИЯ')
    await get_ticket_data(state=state, message=callback.message)


@router.message(F.text, StateFilter(Order_ticket.data_birthday))
async def get_citizenship_other(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_citizenship_other')
    await state.set_state(state=None)
    await state.update_data(citizenship=message.text)
    await get_ticket_data(state=state, message=message)


async def get_ticket_data(state: FSMContext, message: Message):
    logging.info('get_ticket_data')
    data = await state.get_data()
    order_id = data['order_id']
    number = data['number']
    seat_num = data['seat_num']
    fare_name = 'Пассажирский'
    name = data['name']
    document_number = data['document_number']
    document = 'Паспорт гражданина РФ'
    birthday = data['birthday']
    gender = data['gender']
    citizenship = data['citizenship']
    ticket_data = await set_ticket_data(order_id=order_id,
                                        number=number,
                                        seat_num=seat_num,
                                        fare_name=fare_name,
                                        name=name,
                                        document_number=document_number,
                                        document=document,
                                        birthday=birthday,
                                        gender=gender,
                                        citizenship=citizenship)
    await message.answer(text='Данные успешно добавлены',
                         reply_markup=keyboard_pay_ticket())


@router.callback_query(F.data == 'pay_ticket')
async def pay_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'pay_ticket')
    data = await state.get_data()
    order_id = data['order_id']
    reserve = await reserve_order(order_id=order_id)
    amount = reserve['Amount']
    payment = await payment_ticket(order_id=order_id, amount=amount)