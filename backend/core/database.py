import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.core.config import DATABASE_URL

# Remove surrounding quotes if any and strip URL query params that asyncpg won't accept
_raw_url = DATABASE_URL.strip().strip("'\"")

# Ensure the driver is asyncpg if it's a postgres url
if _raw_url.startswith("postgresql://"):
     _raw_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

_db_url = _raw_url.split("?", 1)[0]

# Create an SSL context to pass to asyncpg.connect()
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    _db_url,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": _ssl_context,
        "statement_cache_size": 0,  # Required for Supabase Transaction Pooler
    },
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session