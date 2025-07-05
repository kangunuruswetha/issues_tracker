from datetime import timedelta # Import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # New import for form data
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from app.models.models import User
from app.database.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    authenticate_user, # Ensure this is imported
    get_current_user, # Keep if used for other endpoints
    get_current_active_user, # Keep if used for other endpoints
    get_current_active_admin # Keep if used for other endpoints
)
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES # Ensure this is imported from config

import logging # Ensure logging is imported
logger = logging.getLogger(__name__) # Initialize logger

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------
# Register New User
# ----------------------------
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password and optional role
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role=user.role or "reporter"  # Defaults to "reporter" if not given
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ----------------------------
# Login and Get JWT Token (MODIFIED)
# ----------------------------
@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # Changed from UserLogin to OAuth2PasswordRequestForm
    db: Session = Depends(get_db)
):
    # Use form_data.username and form_data.password
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "roles": user.role}, # Use user.email and user.role from the authenticated user object
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# You might have other endpoints like this for testing current user
# @router.get("/me", response_model=UserResponse)
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user

# @router.get("/me/admin", response_model=UserResponse)
# async def read_users_me_admin(current_user: User = Depends(get_current_active_admin)):
#     return current_user