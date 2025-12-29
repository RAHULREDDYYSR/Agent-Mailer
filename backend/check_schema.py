import asyncio
from sqlalchemy import text
from backend.core.database import get_db

async def check_schema():
    print("Checking 'users' table schema...")
    async for session in get_db():
        try:
            # Query information_schema to get column details
            query = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';")
            result = await session.execute(query)
            rows = result.fetchall()
            print(f"Found {len(rows)} columns:")
            for row in rows:
                print(f"- {row[0]}: {row[1]}")
        except Exception as e:
            print(f"Error checking schema: {e}")
        finally:
            await session.close()
            return

if __name__ == "__main__":
    asyncio.run(check_schema())
