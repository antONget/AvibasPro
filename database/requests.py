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
            await session.commit()

"""TICKETS"""


async def add_ticket(data: dict) -> None:
    logging.info(f'add_ticket')
    async with async_session() as session:
        session.add(Tiket(**data))
        await session.commit()
