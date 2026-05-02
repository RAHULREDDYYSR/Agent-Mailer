import os
from dotenv import load_dotenv
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30