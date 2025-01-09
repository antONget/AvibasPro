from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time, timedelta, datetime
import logging


def keyboard_name(name: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=f'{name}', callback_data=f'name_{name}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_birthday(birthday: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=f'{birthday}', callback_data=f'birthday_{birthday}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_passport(passport: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=f'{passport}', callback_data=f'passport_{passport}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_gender() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Мужской 👦', callback_data='gender_male')
    button_2 = InlineKeyboardButton(text='Женский 👩', callback_data='gender_female')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_citizenship() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='РОССИЯ', callback_data='citizenship_РОССИЯ')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_citizenship_(citizenship: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='РОССИЯ', callback_data='citizenship_РОССИЯ')
    button_2 = InlineKeyboardButton(text=f'{citizenship}', callback_data=f'citizenship_{citizenship}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_email(email: str) -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text=f'{email}', callback_data=f'email_{email}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_pay_ticket() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Купить билет 🎫', callback_data='pay_ticket')
    button_2 = InlineKeyboardButton(text='Добавить багаж 🧳', callback_data='add_luggage')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_get_contact() -> ReplyKeyboardMarkup:
    logging.info("keyboards_get_contact")
    button_1 = KeyboardButton(text='Отправить свой контакт ☎️',
                              request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_payment(payment_url: str, payment_id: int, amount: str) -> InlineKeyboardMarkup:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    button_2 = InlineKeyboardButton(text='Получить билет', callback_data=f'payment_{payment_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard
