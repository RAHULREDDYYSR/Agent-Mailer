import asyncio
from sqlalchemy import text
from backend.core.database import engine

async def fix_schema():
    async with engine.begin() as conn:
        print("Checking/Adding job_text column to job_descriptions...")
        await conn.execute(text("ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS job_text TEXT DEFAULT ''"))
        print("Done.")

if __name__ == "__main__":
    asyncio.run(fix_schema())
