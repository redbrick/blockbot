from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.config import DB_ENABLED, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

if DB_ENABLED:
    engine = create_async_engine(
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=False
    )

    Base = declarative_base()
    Session = async_sessionmaker(bind=engine)

    async def init_db() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

else:
    print("Database disabled due to DB_ENABLED=false in env.")

    async def init_db() -> None:
        pass
