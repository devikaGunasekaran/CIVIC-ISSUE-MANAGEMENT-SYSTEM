from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load Environment Variables
load_dotenv()

from .core.database import engine, Base
from .models.user import User
from .models.complaint import Complaint
from .controllers import auth_controller, complaint_controller, admin_controller, stt_controller, chatbot_controller

# Initialize Database
try:
    Base.metadata.create_all(bind=engine)
    print("[OK] Database Models Initialized")
except Exception as e:
    print(f"[ERROR] Database creation failed: {e}")

app = FastAPI(title="Civic Issue Management System - Structured V1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Controllers/Routers
app.include_router(auth_controller.router)
app.include_router(complaint_controller.router)
app.include_router(admin_controller.router)
app.include_router(stt_controller.router)
app.include_router(chatbot_controller.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Structured Civic Issue Management System API"}
