import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.user_keyboard_order_ticket import keyboard_name, keyboard_pay_ticket, keyboard_gender, \
    keyboard_citizenship, keyboard_birthday, keyboard_passport, keyboard_citizenship_
from services.zeep_soap import add_tickets, set_ticket_data, reserve_order, payment_ticket, get_available_privileges
from config_data.config import Config, load_config
from database.requests import get_user, update_user, UserAttribute
from database.models import User
from utils.error_handling import error_handler
import logging
import re

router = Router()
config: Config = load_config()


class OrderTicket(StatesGroup):
    data_personal = State()
    data_passport = State()
    data_birthday = State()
    citizenship = State()


@router.callback_query(F.data == 'confirm')
@error_handler
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
    user: User = await get_user(tg_id=callback.from_user.id)
    if user.name == 'default':
        await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                         reply_markup=None)
    else:
        await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                         reply_markup=keyboard_name(name=user.name))
    await state.set_state(state=OrderTicket.data_personal)
    await callback.answer()


@router.message(F.text, StateFilter(OrderTicket.data_personal))
async def get_data_personal(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем ФИО пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_personal')
    name_pattern = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$')
    if name_pattern.match(message.text):
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id-1)
        await message.delete()
        await state.update_data(name=message.text)
        await update_user(tg_id=message.from_user.id,
                          attribute=UserAttribute.name,
                          data=message.text)
        await message.answer(text='Укажите ваш пол',
                             reply_markup=keyboard_gender())
    else:
        msg = await message.answer(text='Некорректные введенные данные, пришлите ФИО в формате: Иванов Сергей Игоревич')
        await asyncio.sleep(3)
        await msg.delete()


@router.callback_query(F.data.startswith('name'))
@error_handler
async def get_data_personal(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем подтвержденные ранее введенные ФИО
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_personal')
    name = callback.data.split('_', maxsplit=1)[-1]
    await state.update_data(name=name)
    await callback.message.edit_text(text='Укажите ваш пол',
                                     reply_markup=keyboard_gender())


@router.callback_query(F.data.startswith("gender_"))
async def get_data_gender(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем пол пользователя
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_gender')
    answer = callback.data.split('_')[-1]
    if answer == 'male':
        await state.update_data(gender='Мужской')
        await update_user(tg_id=callback.message.from_user.id,
                          attribute=UserAttribute.gender,
                          data='Мужской')
    else:
        await state.update_data(gender='Женский')
        await update_user(tg_id=callback.message.from_user.id,
                          attribute=UserAttribute.gender,
                          data='Женский')
    user: User = await get_user(tg_id=callback.from_user.id)
    if user.document_number == 'default':
        await callback.message.edit_text(text='Пришлите паспортные данные (например: 12 34 123456',
                                         reply_markup=None)
    else:
        await callback.message.edit_text(text='Пришлите паспортные данные (например: 12 34 123456',
                                         reply_markup=keyboard_passport(passport=user.document_number))
    await state.set_state(OrderTicket.data_passport)
    await callback.answer()


@router.callback_query(F.data.startswith('passport_'))
@error_handler
async def get_data_passport(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем подтвержденные ранее введенные ФИО
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_passport')
    document_number = callback.data.split('_', maxsplit=1)[-1]
    await state.update_data(document_number=document_number)
    user: User = await get_user(tg_id=callback.from_user.id)
    if user.birthday == 'default':
        await callback.message.edit_text(text='Укажите дату вашего рождения, в формате: дд-мм-гггг')
    else:
        await callback.message.edit_text(text='Укажите дату вашего рождения, в формате: дд-мм-гггг',
                                         reply_markup=keyboard_birthday(birthday=user.birthday))
    await state.set_state(OrderTicket.data_birthday)


@router.message(F.text, StateFilter(OrderTicket.data_passport))
async def get_data_pasport(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем паспортнве данные от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_pasport')
    name_pattern = re.compile(r'\b[0-9]{2}\s?[0-9]{2}\s?[0-9]{6}\b')
    if name_pattern.match(message.text):
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
        await message.delete()
        await state.update_data(document_number=message.text)
        await update_user(tg_id=message.from_user.id,
                          attribute=UserAttribute.document_number,
                          data=message.text)
        user: User = await get_user(tg_id=message.from_user.id)
        if user.birthday == 'default':
            await message.answer(text='Укажите дату вашего рождения, в формате: дд-мм-гггг')
        else:
            await message.answer(text='Укажите дату вашего рождения, в формате: дд-мм-гггг',
                                    reply_markup=keyboard_birthday(birthday=user.birthday))
        await state.set_state(OrderTicket.data_birthday)
    else:
        msg = await message.answer(text='Некорректные введенные данные, пришлите данные в формате: 12 34 123456')
        await asyncio.sleep(3)
        await msg.delete()


@router.message(F.text, StateFilter(OrderTicket.data_birthday))
async def get_data_birthday(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_data_pasport')
    birthday_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b')
    if birthday_pattern.match(message.text):
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
        await message.delete()
        await state.update_data(birthday=message.text)
        await update_user(tg_id=message.from_user.id,
                          attribute=UserAttribute.birthday,
                          data=message.text)
        await message.answer(text='Укажите ваше гражданство',
                             reply_markup=keyboard_citizenship())
        await state.set_state(OrderTicket.citizenship)
    else:
        msg = await message.answer(text='Некорректные введенные данные, пришлите данные в формате: дд-мм-гггг')
        await asyncio.sleep(3)
        await msg.delete()


@router.callback_query(F.data.startswith('birthday_'))
@error_handler
async def get_data_birthday(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('get_data_birthday')
    birthday = callback.data.split('_', maxsplit=1)[-1]
    await state.update_data(birthday=birthday)
    user: User = await get_user(tg_id=callback.from_user.id)
    if user.citizenship == 'РОССИЯ':
        await callback.message.edit_text(text='Укажите ваше гражданство',
                                         reply_markup=keyboard_citizenship())
    else:
        await callback.message.edit_text(text='Укажите ваше гражданство',
                                         reply_markup=keyboard_citizenship_(citizenship=user.citizenship))


@router.callback_query(F.data.startswith('citizenship_'))
async def get_citizenship(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'get_citizenship')
    await state.set_state(state=None)
    citizenship = callback.data.split('_')[-1]
    await state.update_data(citizenship=citizenship)
    await update_user(tg_id=callback.from_user.id,
                      attribute=UserAttribute.citizenship,
                      data=citizenship)
    await callback.message.delete()
    await get_ticket_data(state=state, message=callback.message)


@router.message(F.text, StateFilter(OrderTicket.citizenship))
async def get_citizenship_other(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_citizenship_other')
    await state.set_state(state=None)
    await state.update_data(citizenship=message.text)
    await update_user(tg_id=message.from_user.id,
                      attribute=UserAttribute.citizenship,
                      data=message.text)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await state.update_data(document_number=message.text)
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
    available_privileges = await get_available_privileges(order_id=order_id,
                                                          ticket_number=number)
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