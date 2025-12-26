from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.database import get_db
from backend.models.user import User
from backend.schemas.auth import LoginRequest, TokenResponse
from backend.core.security import create_access_token, authenticate_user
from backend.utils.password_hash import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post('/login', response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.username == payload.username)
    )
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )
    token = create_access_token(username=user.username, user_id=str(user.id), role=user.role)
    return TokenResponse(access_token=token, token_type="bearer")


@router.post('/token', response_model=TokenResponse)
async def login_for_access_token(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(username=user.username, user_id=str(user.id), role=user.role)
    return TokenResponse(access_token=token, token_type="bearer")