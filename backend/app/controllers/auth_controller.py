from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.user import UserCreate, UserResponse
from ..schemas.complaint import BaseModel # Using generic BaseModel for Token or just define here
from pydantic import BaseModel as TokenSchema # Temporary
from ..services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(TokenSchema):
    access_token: str
    token_type: str

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user)

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login(db, form_data.username, form_data.password)

@router.post("/social-login", response_model=Token)
def social_login(social_data: dict, db: Session = Depends(get_db)):
    return auth_service.social_login(db, social_data)
