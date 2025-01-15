from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}", echo=False)


Base = declarative_base()
Session = sessionmaker(bind=engine)


# Issue with db on startup recommended drop all tables
def init_db():
    Base.metadata.create_all(engine)
