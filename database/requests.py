import logging
import datetime
from dataclasses import dataclass
from aiogram.types import Message, ChatPermissions
from database.models import async_session
from database.models import User
from sqlalchemy import select
from aiogram import Bot
from config_data.config import Config, load_config

from sqlalchemy import desc

config: Config = load_config()


"""USER"""


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
