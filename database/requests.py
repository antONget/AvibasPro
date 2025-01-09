import logging
import datetime
from dataclasses import dataclass
from aiogram.types import Message, ChatPermissions
from database.models import async_session
from database.models import User, Tiket
from sqlalchemy import select
from aiogram import Bot
from config_data.config import Config, load_config

from sqlalchemy import desc

config: Config = load_config()


"""USER"""


@dataclass
class UserAttribute:
    name = "name"
    document = "document"
    document_number = "document_number"
    birthday = "birthday"
    gender = "gender"
    citizenship = "citizenship"
    phone = "phone"
    email = "email"


async def add_user(data: dict) -> None:
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()


async def get_user(tg_id: int) -> User:
    logging.info(f'get_user')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_username(username: str) -> User:
    logging.info(f'get_user_username')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.username == username))


async def update_user(tg_id: int, attribute: UserAttribute, data: str) -> None:
    logging.info(f'get_user_username')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            if attribute == 'name':
                user.name = data
            elif attribute == 'document':
                user.document = data
            elif attribute == 'document_number':
                user.document_number = data
            elif attribute == 'birthday':
                user.birthday = data
            elif attribute == 'gender':
                user.gender = data
            elif attribute == 'citizenship':
                user.citizenship = data
            elif attribute == 'email':
                user.email = data
            elif attribute == 'phone':
                user.phone = data
            await session.commit()

"""TICKETS"""


@dataclass()
class StatusTicket:
    payment = "payment"
    reserve = "reserve"
    cancel = "cancel"
    refund = "refund"


async def add_ticket(data: dict) -> None:
    logging.info(f'add_ticket')
    async with async_session() as session:
        session.add(Tiket(**data))
        await session.commit()


async def update_ticket(id_order: str, status_payment: str, data_ticket: str = None) -> None:
    logging.info(f'update_ticket')
    async with async_session() as session:
        ticket = await session.scalar(select(Tiket).where(Tiket.id_order == id_order))
        if ticket:
            if data_ticket:
                ticket.data_ticket = data_ticket
            ticket.status_payment = status_payment
            await session.commit()


async def update_cancellation_details(id_order: str, cancellation_details: str) -> None:
    logging.info(f'update_cancellation_details')
    async with async_session() as session:
        ticket = await session.scalar(select(Tiket).where(Tiket.id_order == id_order))
        if ticket:
            ticket.cancellation_details = cancellation_details
            await session.commit()


async def get_tickets_user(tg_id: int) -> list[Tiket]:
    logging.info('get_tickets_user')
    async with async_session() as session:
        tickets = await session.scalars(select(Tiket).where(Tiket.tg_id == tg_id, Tiket.status_payment == StatusTicket.payment))
        list_ticket = [ticket for ticket in tickets]

        if list_ticket:
            return list_ticket
        else:
            return []


async def get_ticket_user_id_order(id_order: str) -> Tiket:
    """
    Получение информации о билете по его id_order
    :param id_order:
    :return:
    """
    logging.info('get_ticket_user_id_order')
    async with async_session() as session:
        return await session.scalar(select(Tiket).where(Tiket.id_order == id_order))
