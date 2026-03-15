from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.user import UserResponse, UserUpdate
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the currently authenticated user's profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the currently authenticated user's profile (phone, email)."""
    if user_update.phone is not None:
        # Check uniqueness if another user already has this phone
        existing = db.query(User).filter(
            User.phone == user_update.phone,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already in use by another account.")
        current_user.phone = user_update.phone

    if user_update.email is not None:
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use by another account.")
        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)
    return current_user
