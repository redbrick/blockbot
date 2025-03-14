from sqlalchemy import BigInteger, Integer, SmallInteger
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=False
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


Session = async_sessionmaker(bind=engine)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# TODO: add reprs?


class StarboardSettings(Base):
    __tablename__ = "starboard_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True)
    channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    threshold: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=3)
    error: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=None)


class Starboard(Base):
    __tablename__ = "starboard"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, autoincrement=True
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stars: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    starboard_channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    starboard_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
