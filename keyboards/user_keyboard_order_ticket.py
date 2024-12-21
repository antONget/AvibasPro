from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time, timedelta, datetime
import logging


def keyboard_gender() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Мужской 👦', callback_data='gender_male')
    button_2 = InlineKeyboardButton(text='Женский 👩', callback_data='gender_female')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_citizenship() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='РОССИЯ', callback_data='citizenship_RUSSIA')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_pay_ticket() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(text='Купить билет', callback_data='pay_ticket')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard
