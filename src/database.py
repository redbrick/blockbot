from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=False)


Base = declarative_base()
Session = async_sessionmaker(bind=engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
