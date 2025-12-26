from datetime import datetime, timedelta
from backend.core.config import JWT_ALGORITHM, JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from backend.core.database import get_db
from backend.models.user import User

security = HTTPBearer()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(username: str, user_id: str, role: str) -> str:
    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)




async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: AsyncSession = Depends(get_db),
) -> User:
    try: 
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> bool:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalars().first()
    if not user:
        return False
    from backend.utils.password_hash import verify_password
    if not verify_password(password, user.password_hash):
        return False
    return user