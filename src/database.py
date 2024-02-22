from sqlalchemy import BigInteger, Column, Integer, SmallInteger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

from src.config import POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER, POSTGRES_DB_NAME


Base = declarative_base()

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


engine = create_async_engine(
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
)
