from fastapi import FastAPI
from backend.routers import users
from backend.routers import auth
from backend.routers import generation

app = FastAPI(title="Agent Mailer Backend", version="1.0.0")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(generation.router)
