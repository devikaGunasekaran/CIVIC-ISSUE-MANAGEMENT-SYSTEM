from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repositories.user_repository import user_repository
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from ..core.config import settings

class AuthService:
    def register_user(self, db: Session, user_in: UserCreate):
        import time
        start = time.time()
        
        print(f"[AUTH] Checking username: {user_in.username}")
        db_user = user_repository.get_by_username(db, user_in.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        print(f"[AUTH] Checking email: {user_in.email}")
        db_email = user_repository.get_by_email(db, user_in.email)
        if db_email:
             raise HTTPException(status_code=400, detail="Email already registered")

        print(f"[AUTH] Hashing password...")
        hash_start = time.time()
        hashed_pw = get_password_hash(user_in.password)
        print(f"[AUTH] Hashing took: {time.time() - hash_start:.4f}s")
        
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            phone=user_in.phone if hasattr(user_in, 'phone') else None,
            hashed_password=hashed_pw,
            area=user_in.area,
            role="citizen"
        )
        print(f"[AUTH] Saving user to DB...")
        result = user_repository.create(db, new_user)
        print(f"[AUTH] Total registration time: {time.time() - start:.4f}s")
        return result

    def login(self, db: Session, username: str, password: str):
        db_user = user_repository.get_by_username(db, username)
        if not db_user or not verify_password(password, db_user.hashed_password):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role, "area": db_user.area})
        return {"access_token": access_token, "token_type": "bearer"}

    def social_login(self, db: Session, social_data: dict):
        provider = social_data.get("provider", "google")
        identifier = social_data.get("email") or social_data.get("phone")
        
        if not identifier:
            raise HTTPException(status_code=400, detail="Identifier (email or phone) is required")
            
        # Check if user exists
        user = user_repository.get_by_username(db, identifier)
        if not user:
             user = user_repository.get_by_email(db, identifier)

        if not user:
            user = User(
                username=identifier,
                email=identifier if "@" in identifier else f"{identifier}@phone.local",
                role="citizen",
                hashed_password=get_password_hash(f"social-{provider}-placeholder")
            )
            user_repository.create(db, user)
        
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role, "area": user.area}
        )
        return {"access_token": access_token, "token_type": "bearer"}

auth_service = AuthService()
