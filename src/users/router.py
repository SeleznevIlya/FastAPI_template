from typing import List, Optional

from fastapi import APIRouter, Depends, Response, Request, status

from .schemas import UserCreate, User
from .service import UserService
# from .models import UserModel


auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/user", tags=["user"])


@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate) -> User:
    return await UserService.create_new_user(user)
    