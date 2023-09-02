from typing import List, Optional


from fastapi import APIRouter, Depends, Response, Request, status






auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/user", tags=["user"])















