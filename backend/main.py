from fastapi import FastAPI
from backend.routers import users
from backend.routers import auth
from backend.routers import generation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Agent Mailer Backend", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Agent Mailer API is running"}


# Adjust allowed origins after you know your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://your-frontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(generation.router)
