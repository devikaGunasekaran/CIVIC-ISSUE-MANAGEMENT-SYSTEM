from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, reports, admin, stt
import models
from database import engine

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Civic Issue Management System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(admin.router)
app.include_router(stt.router)

# Create tables if not exist (in production use Alembic)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Civic Issue Management System API"}
