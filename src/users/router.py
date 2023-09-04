from typing import List, Optional

from fastapi import APIRouter, Depends, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import UserCreate, User, Token
from .service import UserService, AuthService
from ..exceptions import InvalidCredentialsException
from ..config import settings
from .models import UserModel
from .dependencies import get_current_active_user


auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/user", tags=["user"])


@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate) -> User:
    return await UserService.create_new_user(user)


@auth_router.post("/login")
async def login(
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = await AuthService.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise InvalidCredentialsException
    
    token = await AuthService.create_token(user.id)
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,
        httponly=True
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS*30*24*60,
        httponly=True
    )
    return token


@auth_router.post("/logout")
async def logout(request: Request,
                 response: Response,
                 user: UserModel = Depends(get_current_active_user)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthService.logout(request.cookies.get("refresh_token"))
    return {"message": "Logged out successfully"}
