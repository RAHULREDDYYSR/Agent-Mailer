import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.core.config import DATABASE_URL

# Remove surrounding quotes if any and strip URL query params that asyncpg won't accept
_raw_url = DATABASE_URL.strip().strip("'\"")
_db_url = _raw_url.split("?", 1)[0]

# Create an SSL context to pass to asyncpg.connect()
_ssl_context = ssl.create_default_context()
# You can customize the SSL context if you need to set certificates, etc.

engine = create_async_engine(
    _db_url,
    echo=True,
    pool_pre_ping=True,
    connect_args={"ssl": _ssl_context},
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Bass(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session