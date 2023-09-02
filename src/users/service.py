import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt

from .utils import is_valid_password
from .schemas import Token
from ..config import settings
from ..database import async_session_maker
from .repository import RefreshSessionRepository, UserRepository
from .schemas import RefreshSessionCreate, RefreshSessionUpdate
from .models import UserModel, RefreshSessionModel
from ..exceptions import InvalidTokenException, TokenExpiredException, InvalidCredentialsException



class AuthService:
    
    @classmethod
    async def create_token(cls, user_id: uuid.UUID) -> Token:
        access_token = cls._create_access_token(user_id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = cls._create_refresh_token()

        async with async_session_maker() as session:
            await RefreshSessionRepository.add(
                session,
                RefreshSessionCreate(
                    refresh_token=refresh_token, 
                    expires_in=refresh_token_expires.total_seconds(), 
                    user_id=user_id
                )
            )
            await session.commit()
        
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    @classmethod
    async def refresh_token(cls, token: uuid.UUID) -> Token:
        async with async_session_maker() as session:
            refresh_session = await RefreshSessionRepository.find_one_or_none(session, RefreshSessionModel.refresh_token==token)
            if refresh_session is None:
                raise InvalidTokenException
            if datetime.now(timezone.utc) >= refresh_session.created_at + timedelta(seconds=refresh_session.expires_in):
                await RefreshSessionRepository.delete(session, id=refresh_session.id)
                raise TokenExpiredException

            user = await UserRepository.find_one_or_none(session, id=refresh_session.id)
            if user is None:
                raise InvalidTokenException
            
            access_token = cls._create_access_token(user.id)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = cls._create_refresh_token()

            await RefreshSessionRepository.update(
                session,
                RefreshSessionModel.id==refresh_session.id,
                obj_in=RefreshSessionUpdate(
                    refresh_token=refresh_token,
                    expires_in=refresh_token_expires.total_seconds()
                )
            )
            await session.commit()
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    @classmethod
    async def logout(cls, token: uuid.UUID) -> None:
        async with async_session_maker() as session:
            refresh_session = RefreshSessionRepository.find_one_or_none(session, RefreshSessionModel.refresh_token==token)
            if refresh_session:
                await RefreshSessionRepository.delete(session, id=refresh_session.id)
            await session.commit()

    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> Optional[UserModel]:
        async with async_session_maker() as session:
            db_user = await UserRepository.find_one_or_none(session, email=email)
        if db_user and is_valid_password(password, db_user.hashed_password):
            return db_user
        return

    @classmethod
    async def abort_all_session(cls, user_id: uuid.UUID) -> None:
        async with async_session_maker() as session:
            await RefreshSessionRepository.delete(session, RefreshSessionModel.user_id==user_id)
            await session.commit()

    @classmethod
    async def _create_access_token(cls, user_id: uuid.UUID) -> str:
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return f"Bearer {encoded_jwt}"

    @classmethod
    async def _create_refresh_token(cls) -> str:
        return uuid.uuid4()


class UserService:
    pass
