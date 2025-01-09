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
    phone: Mapped[str] = mapped_column(String(), default='default')
    email: Mapped[str] = mapped_column(String(), default='default')


class Tiket(Base):
    __tablename__ = 'tikets'
    id_ticket: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    id_order: Mapped[str] = mapped_column(String())
    ticket_number: Mapped[str] = mapped_column(String())
    amount: Mapped[str] = mapped_column(String(), default='default')
    data_ticket: Mapped[str] = mapped_column(String(), default='default')
    id_departure: Mapped[str] = mapped_column(String(), default='default')
    departure: Mapped[str] = mapped_column(String(), default='default')
    id_destination: Mapped[str] = mapped_column(String(), default='default')
    destination: Mapped[str] = mapped_column(String(), default='default')
    departure_time: Mapped[str] = mapped_column(String(), default='default')
    departure_data: Mapped[str] = mapped_column(String(), default='default')
    arrival_time: Mapped[str] = mapped_column(String(), default='default')
    arrival_data: Mapped[str] = mapped_column(String(), default='default')
    payment_id: Mapped[str] = mapped_column(String(), default='default')
    status_payment: Mapped[str] = mapped_column(String(), default='default')
    cancellation_details: Mapped[str] = mapped_column(String(), default='default')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
