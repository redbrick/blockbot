from sqlalchemy import BigInteger, Column, Integer, SmallInteger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=False
)

Base = declarative_base()
Session = async_sessionmaker(bind=engine)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# TODO: add reprs?


class StarboardSettings(Base):
    __tablename__ = "starboard_settings"

    guild = Column(BigInteger, nullable=False, primary_key=True)
    channel = Column(BigInteger, nullable=True)
    threshold = Column(SmallInteger, nullable=False, default=3)


class Starboard(Base):
    __tablename__ = "starboard"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    channel = Column(BigInteger, nullable=False)
    message = Column(BigInteger, nullable=False)
    stars = Column(SmallInteger, nullable=False)
    starboard_channel = Column(BigInteger, nullable=False)
    starboard_message = Column(BigInteger, nullable=False)
    starboard_stars = Column(SmallInteger, nullable=False)
