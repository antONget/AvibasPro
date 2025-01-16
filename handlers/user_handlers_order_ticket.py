import asyncio
import datetime

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from keyboards.user_keyboard_order_ticket import keyboard_name, keyboard_pay_ticket, keyboard_gender, \
    keyboard_citizenship, keyboard_birthday, keyboard_passport, keyboard_citizenship_, keyboards_get_contact, \
    keyboard_email, keyboard_payment, keyboard_confirm_ticket_data
from keyboards.user_keyboard_select_station import keyboard_main_button, keyboard_major_button
from services.zeep_soap import add_tickets, set_ticket_data, reserve_order, payment_ticket
from services.payments import create_payment, check_payment
from services.smtp_email import send_email
from services.exel_to_pdf import excel_to_pdf
from config_data.config import Config, load_config
from database.requests import get_user, update_user, UserAttribute, add_ticket, StatusTicket, update_ticket
from database.models import User
from utils.error_handling import error_handler
from filters.filter import validate_russian_phone_number, validate_email
from services.write_exel import get_boarding_receipt
import logging
import re
import json

router = Router()
config: Config = load_config()


class OrderTicket(StatesGroup):
    data_personal = State()
    data_passport = State()
    data_birthday = State()
    gender = State()
    citizenship = State()
    email = State()
    phone = State()


@router.callback_query(F.data == 'confirm')
@error_handler
async def order_ticket(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
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
        await state.set_state(state=OrderTicket.data_personal)
        await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                         reply_markup=None)
    else:
        name = user.name
        gender = user.gender
        document_number = user.document_number
        birthday = user.birthday
        citizenship = user.citizenship
        phone = user.phone
        email = user.email

        await callback.message.edit_text(text=f'Подтвердите или измените ранее введенные данные:\n'
                                              f'<b>ФИО:</b> {name}\n'
                                              f'<b>Пол:</b> {gender}\n'
                                              f'<b>Номер документа:</b> {document_number}\n'
                                              f'<b>Дата рождения:</b> {birthday}\n'
                                              f'<b>Гражданство:</b> {citizenship}\n'
                                              f'<b>Номер телефона:</b> {phone}\n'
                                              f'<b>Email:</b> {email}\n',
                                         reply_markup=keyboard_confirm_ticket_data())
    await callback.answer()


@router.callback_query(F.data == 'ticket_data_confirm')
@error_handler
async def ticket_data_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Подтвержденные ранее введенных данных
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('ticket_data_confirm')
    data = await state.get_data()
    user: User = await get_user(tg_id=callback.from_user.id)
    name = user.name
    gender = user.gender
    document_number = user.document_number
    birthday = user.birthday
    citizenship = user.citizenship
    phone = user.phone
    email = user.email
    fare_name = 'Пассажирский'
    document = 'Паспорт гражданина РФ'
    ticket_data = await set_ticket_data(order_id=data['order_id'],
                                        number=data['number'],
                                        seat_num=data['seat_num'],
                                        fare_name=fare_name,
                                        name=name,
                                        document_number=document_number,
                                        document=document,
                                        birthday=birthday,
                                        gender=gender,
                                        citizenship=citizenship)
    await callback.message.edit_text(text='Данные успешно добавлены',
                                     reply_markup=keyboard_pay_ticket())


@router.callback_query(F.data == 'ticket_data_change')
@error_handler
async def ticket_data_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Правка ранее введенных данных
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('ticket_data_change')
    user: User = await get_user(tg_id=callback.from_user.id)
    await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                     reply_markup=keyboard_name(name=user.name))
    await state.set_state(OrderTicket.data_personal)


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
        await state.set_state(OrderTicket.gender)
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
    await state.set_state(OrderTicket.gender)
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
        await update_user(tg_id=callback.from_user.id,
                          attribute=UserAttribute.gender,
                          data='Мужской')
    else:
        await state.update_data(gender='Женский')
        await update_user(tg_id=callback.from_user.id,
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
    Получаем паспортные данные от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_data_pasport')
    name_pattern = re.compile(r'\b[0-9]{2}\s{1}[0-9]{2}\s{1}[0-9]{6}\b')
    if name_pattern.match(message.text):
        try:
            await bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
            await message.delete()
        except:
            pass
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
    logging.info('get_data_birthday')
    birthday_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b')
    if birthday_pattern.match(message.text):
        try:
            await bot.delete_message(chat_id=message.chat.id,
                                     message_id=message.message_id - 1)
            await message.delete()
        except:
            pass
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
    await state.set_state(state=OrderTicket.citizenship)


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
    await callback.message.answer(text="Укажите ваш номер телефона или нажмите внизу 👇 Отправить свой контакт ☎️",
                                  reply_markup=keyboards_get_contact())
    await state.set_state(OrderTicket.phone)
    # await get_ticket_data(state=state, message=callback.message)


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
    await message.answer(text="Укажите ваш номер телефона или нажмите внизу 👇 Отправить свой контакт ☎️",
                         reply_markup=keyboards_get_contact())
    await state.set_state(OrderTicket.phone)
    # await get_ticket_data(state=state, message=message)


@router.message(StateFilter(OrderTicket.phone))
async def get_phone_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем номер телефона проверяем его на валидность и заносим его в БД
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    await message.delete()
    # если номер телефона отправлен через кнопку "Поделится"
    if message.contact:
        phone = str(message.contact.phone_number)
    # если введен в поле ввода
    else:
        phone = message.text
        # проверка валидности отправленного номера телефона, если не валиден просим ввести его повторно
        if not validate_russian_phone_number(phone):
            await bot.edit_message_text(text="Неверный формат номера, повторите ввод.")
            return
    await update_user(tg_id=message.from_user.id,
                      attribute=UserAttribute.phone,
                      data=phone)
    await state.update_data(phone=phone)
    user: User = await get_user(tg_id=message.from_user.id)
    if user.email == 'default':
        await message.answer(text="Укажите ваш email для отправки билета",
                             reply_markup=keyboard_major_button())
    else:
        msg = await message.answer('---',
                                   reply_markup=keyboard_major_button())
        await message.answer(text="Укажите ваш email для отправки билета",
                             reply_markup=keyboard_email(email=user.email))
    await state.set_state(state=OrderTicket.email)


@router.callback_query(F.data.startswith('email#'))
async def get_email(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'get_email')
    await callback.message.delete()
    await state.set_state(state=None)
    email = callback.data.split('#')[-1]
    await state.update_data(email=email)
    await update_user(tg_id=callback.from_user.id,
                      attribute=UserAttribute.email,
                      data=email)
    await get_ticket_data(state=state, message=callback.message)
    await callback.answer()


@router.message(F.text, StateFilter(OrderTicket.email))
async def get_email_other(message: Message, state: FSMContext, bot: Bot):
    logging.info('get_email_other')
    await state.set_state(state=None)
    email = message.text
    # проверка валидности отправленного номера телефона, если не валиден просим ввести его повторно
    if not validate_email(email):
        await bot.edit_message_text(text="Неверный формат email.")
        return
    await state.update_data(email=email)
    await update_user(tg_id=message.from_user.id,
                      attribute=UserAttribute.email,
                      data=email)
    await get_ticket_data(state=state, message=message)


async def get_ticket_data(state: FSMContext, message: Message):
    logging.info('get_ticket_data')
    data = await state.get_data()
    order_id = data['order_id']
    number = data['number']
    seat_num = data['seat_num']
    fare_name = 'Пассажирский'
    await state.update_data(fare_name=fare_name)
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
    await state.update_data(amount=amount)
    user: User = await get_user(tg_id=callback.from_user.id)
    description = f'Автобусный билет: {user.name}'
    payment_url, payment_id = create_payment(amount=amount,
                                             description=description,
                                             full_name=user.name,
                                             user_tg_id=callback.from_user.id,
                                             message_order_id=callback.message.message_id,
                                             email=user.email,
                                             phone=user.phone)
    await callback.message.edit_text(text=f'Оплатите билет, после оплаты нажмите на кнопку «Получить билет» ⬇️',
                                     reply_markup=keyboard_payment(payment_url=payment_url,
                                                                   payment_id=payment_id,
                                                                   amount=amount))
    ticket_departure_time = reserve["Tickets"][0]["DepartureTime"]
    departure_time = str(ticket_departure_time.strftime("%H:%M"))
    departure_data = str(ticket_departure_time.strftime("%d.%m.%Y"))
    ticket_arrival_time = reserve["Tickets"][0]["ArrivalTime"]
    arrival_time = str(ticket_arrival_time.strftime("%H:%M"))
    arrival_data = str(ticket_arrival_time.strftime("%d.%m.%Y"))
    ticket_data = {"tg_id": callback.from_user.id,
                   "id_order": reserve["Number"],
                   "ticket_number": reserve["Tickets"][0]["Number"],
                   "amount": float(reserve['Amount']),
                   "id_departure": reserve["Trip"]["Departure"]["Id"],
                   "departure": reserve["Trip"]["Departure"]["Name"],
                   "id_destination": reserve["Trip"]["Destination"]["Id"],
                   "destination": reserve["Trip"]["Destination"]["Name"],
                   "departure_time": departure_time,
                   "departure_data": departure_data,
                   "arrival_time": arrival_time,
                   "arrival_data": arrival_data,
                   "payment_id": payment_id,
                   "status_payment": StatusTicket.reserve}
    await add_ticket(data=ticket_data)
    await callback.answer()


@router.callback_query(F.data.startswith('payment_'))
async def get_ticket(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'get_ticket')
    payment_id = callback.data.split('_')[1]
    result = check_payment(payment_id=payment_id)
    # result = 'succeeded'
    if result == 'succeeded':
        await callback.message.delete()
        await callback.message.answer(text='Идет подготовка билета. Ожидайте ⏳...')
        await bot.send_chat_action(chat_id=callback.from_user.id,
                                   action="typing")
        data = await state.get_data()
        order_id = data['order_id']
        amount = data['amount']
        payment = await payment_ticket(order_id=order_id, amount=amount)
        ticket_data = payment["Tickets"][0]["Date"]
        data_ticket = str(ticket_data.strftime("%d.%m.%Y %H:%M"))
        ticket_departure_time = payment["Tickets"][0]["DepartureTime"]
        departure_time = str(ticket_departure_time.strftime("%H:%M"))
        departure_data = str(ticket_departure_time.strftime("%d.%m.%Y"))
        ticket_arrival_time = payment["Tickets"][0]["ArrivalTime"]
        arrival_time = str(ticket_arrival_time.strftime("%H:%M"))
        arrival_data = str(ticket_arrival_time.strftime("%d.%m.%Y"))
        dict_check_ticket = {"B5:B6": f'{str(payment["Trip"]["RouteName"])}',
                             "B11:B12": f'{str(payment["Tickets"][0]["Number"])},'
                                        f' тариф {str(payment["Tickets"][0]["FareName"])},'
                                        f' заказ {str(payment["Number"])}, оплачен {data_ticket}',
                             "B14:B15": f'{str(payment["Tickets"][0]["PassengerName"])},'
                                        f' {str(payment["Tickets"][0]["PassengerDoc"])}',
                             "B17:B18": f'{float(payment["Amount"])} руб.',
                             "E1:H1": f'*{str(payment["Tickets"][0]["Number"])}*',
                             "D2:G2": str(payment["Tickets"][0]["FareName"]),
                             "H2": f'Место {str(payment["Tickets"][0]["SeatNum"])}',
                             "F5:F6": departure_time,
                             "G5:H6": departure_data,
                             "F7:H9": str(payment["Tickets"][0]["Departure"]["Name"]),
                             "F10:H13": f'{str(payment["Trip"]["Bus"]["Model"])},'
                                        f' {str(payment["Trip"]["Bus"]["LicencePlate"])}\n'
                                        f'{str(payment["Trip"]["Departure"]["Address"])}\n'
                                        f'{str(payment["Trip"]["Departure"]["Phone"]) if payment["Trip"]["Departure"]["Phone"] else ""}',
                             "F17:F18": arrival_time,
                             "G17:H17": arrival_data,
                             "F19:H21": str(payment["Tickets"][0]["Destination"]["Name"]),
                             "F22:H24": f'{str(payment["Trip"]["Destination"]["Address"])}\n'
                                        f'{str(payment["Trip"]["Destination"]["Phone"]) if payment["Trip"]["Destination"]["Phone"] else""}'}
        # print(dict_check_ticket)
        # with open(file='check_ticket.json',
        #           mode='w',
        #           encoding='utf-8') as file:
        #     json.dump(dict_check_ticket, file)
        ticket_data = {"amount": float(payment['Amount']),
                       "data_ticket": data_ticket,
                       "id_departure": payment["Trip"]["Departure"]["Id"],
                       "departure": payment["Trip"]["Departure"]["Name"],
                       "id_destination": payment["Trip"]["Destination"]["Id"],
                       "destination": payment["Trip"]["Destination"]["Name"],
                       "departure_time": payment["DepartureTime"],
                       "departure_data": departure_data,
                       "arrival_time": arrival_time,
                       "arrival_data": arrival_data,
                       "payment_id": payment_id,
                       "status_payment": StatusTicket.payment}
        await update_ticket(id_order=payment["Number"],
                            data_ticket=data_ticket,
                            status_payment=StatusTicket.payment)
        await get_boarding_receipt(dict_check_ticket=dict_check_ticket, user_id=callback.from_user.id)
        excel_to_pdf(input_file=f'TICKET/{callback.from_user.id}.xlsx',
                     output_file=f'TICKET/{callback.from_user.id}.pdf')
        # await callback.answer(text='Платеж прошел успешно', show_alert=True)
        user: User = await get_user(tg_id=callback.from_user.id)
        await send_email(to_email=user.email,
                         message_email=f'Билет: *{order_id}*\n'
                                       f'Отправление: {payment["Trip"]["Departure"]["Name"]}\n'
                                       f'{departure_data} {departure_time}\n'
                                       f'Прибытие: {payment["Trip"]["Destination"]["Name"]}\n'
                                       f'{arrival_data} {arrival_time}\n'
                                       f'Место: {payment["Tickets"][0]["SeatNum"]}',
                         tg_user=callback.from_user.id)
        await callback.message.answer_document(document=FSInputFile(path=f'TICKET/{callback.from_user.id}.pdf'),
                                               caption=f'Ваш билет *{order_id}*\n'
                                                       f'Он также направлен вам на email')
    else:
        await callback.message.answer(text='Платеж не подтвержден, если вы совершили платеж, то попробуйте запросить'
                                           ' билет немного позднее')
    await callback.answer()


@router.callback_query(F.data == 'back_dialog_personal')
@error_handler
async def back_dialog(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('back_dialog')
    current_state = (await state.get_state()).split(':')[-1]
    # data_passport = State()
    # data_birthday = State()
    # citizenship = State()
    # email = State()
    # phone = State()
    if current_state == 'data_personal':
        user: User = await get_user(tg_id=callback.from_user.id)
        await state.set_state(state=OrderTicket.data_personal)
        if user.name == 'default':
            await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                             reply_markup=None)
        else:
            name = user.name
            gender = user.gender
            document_number = user.document_number
            birthday = user.birthday
            citizenship = user.citizenship
            phone = user.phone
            email = user.email

            await callback.message.edit_text(text=f'Подтвердите или измените ранее введенные данные:\n'
                                                  f'<b>ФИО:</b> {name}\n'
                                                  f'<b>Пол:</b> {gender}\n'
                                                  f'<b>Номер документа:</b> {document_number}\n'
                                                  f'<b>Дата рождения:</b> {birthday}\n'
                                                  f'<b>Гражданство:</b> {citizenship}\n'
                                                  f'<b>Номер телефона:</b> {phone}\n'
                                                  f'<b>Email:</b> {email}\n',
                                             reply_markup=keyboard_confirm_ticket_data())
    elif current_state == 'gender':
        user: User = await get_user(tg_id=callback.from_user.id)
        await callback.message.edit_text(text='Пришлите Ваше ФИО (например: Иванов Сергей Игоревич)',
                                         reply_markup=keyboard_name(name=user.name))
        await state.set_state(OrderTicket.data_personal)
    elif current_state == 'data_passport':
        await callback.message.edit_text(text='Укажите ваш пол',
                                         reply_markup=keyboard_gender())
    elif current_state == 'data_birthday':
        user: User = await get_user(tg_id=callback.from_user.id)
        if user.document_number == 'default':
            await callback.message.edit_text(text='Пришлите паспортные данные (например: 12 34 123456',
                                             reply_markup=None)
        else:
            await callback.message.edit_text(text='Пришлите паспортные данные (например: 12 34 123456',
                                             reply_markup=keyboard_passport(passport=user.document_number))
        await state.set_state(OrderTicket.data_passport)
    elif current_state == 'citizenship':
        user: User = await get_user(tg_id=callback.from_user.id)
        if user.birthday == 'default':
            await callback.message.edit_text(text='Укажите дату вашего рождения, в формате: дд-мм-гггг')
        else:
            await callback.message.edit_text(text='Укажите дату вашего рождения, в формате: дд-мм-гггг',
                                             reply_markup=keyboard_birthday(birthday=user.birthday))
        await state.set_state(OrderTicket.data_birthday)
    elif current_state == 'email':
        await callback.message.delete()
        await callback.message.answer(text="Укажите ваш номер телефона или нажмите внизу 👇 Отправить свой контакт ☎️",
                                      reply_markup=keyboards_get_contact())
        await state.set_state(OrderTicket.phone)
    await callback.answer()
