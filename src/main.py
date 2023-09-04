from fastapi import FastAPI

from src.users.router import auth_router

app = FastAPI()

app.include_router(auth_router)

