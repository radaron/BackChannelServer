import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.utils.logger import logger

DB_DIR = Path(__file__).parent.parent / "db"

DB_PATH = DB_DIR / "backchannel.db"
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_db(retries: int = 5, delay: int = 5):
    logger.info("Initializing database...")
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            break
        except Exception as e:  # pylint: disable=broad-exception-caught
            if attempt < retries - 1:
                logger.warning(
                    "Database connection failed. Retrying in %s seconds...", delay
                )
                await asyncio.sleep(delay)
            else:
                logger.error("Database connection failed. Maximum retries reached.")
                raise e


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def open_db_session() -> AsyncSession:
    return AsyncSessionLocal()
