from sqlalchemy import String, Integer, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


# Создаем асинхронный движок
engine = create_async_engine("sqlite+aiosqlite:///database/db.sqlite3", echo=False)
# Настраиваем фабрику сессий
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass



class User(Base):
    __tablename__ = 'users'
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(), default='default')
    document: Mapped[str] = mapped_column(String(), default='default')
    document_number: Mapped[str] = mapped_column(String(), default='default')
    birthday: Mapped[str] = mapped_column(String(), default='default')
    gender: Mapped[str] = mapped_column(String(), default='default')
    citizenship: Mapped[str] = mapped_column(String(), default='default')

class Tiket(Base):
    __tablename__ = 'tikets'

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_order: Mapped[str] = mapped_column(String())
    ticket_number: Mapped[str] = mapped_column(String())


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
