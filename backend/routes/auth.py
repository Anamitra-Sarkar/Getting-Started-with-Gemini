"""
Simple authentication routes for development/testing without Firebase.
In production, Firebase authentication should be used.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import jwt
import os
from sqlmodel import Session, select
from ..models import engine, Account

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Secret key for JWT - should be in environment variable in production
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
# Development password - change in production
DEV_PASSWORD = os.getenv("DEV_AUTH_PASSWORD", "devpass123")


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class AuthResponse(BaseModel):
    token: str
    user: dict


def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=AuthResponse)
def register(body: RegisterRequest):
    """Register a new user - simple implementation for development"""
    with Session(engine) as session:
        # Check if user already exists
        existing = session.exec(
            select(Account).where(Account.user_id == body.email).limit(1)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new account
        account = Account(
            user_id=body.email,
            credits=100.0,  # Give new users 100 credits
            role="member"
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        
        # Create token
        token = create_access_token({
            "uid": body.email,
            "email": body.email,
            "name": body.name
        })
        
        return {
            "token": token,
            "user": {
                "uid": body.email,
                "email": body.email,
                "name": body.name,
                "credits": account.credits
            }
        }


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest):
    """Login user - simple implementation for development"""
    with Session(engine) as session:
        # Check if account exists
        account = session.exec(
            select(Account).where(Account.user_id == body.email).limit(1)
        ).first()
        
        if not account:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password - in development, use DEV_PASSWORD
        # In production, this should verify against a password hash
        if body.password != DEV_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create token
        token = create_access_token({
            "uid": body.email,
            "email": body.email,
            "name": body.email.split("@")[0]  # Simple name from email
        })
        
        return {
            "token": token,
            "user": {
                "uid": body.email,
                "email": body.email,
                "name": body.email.split("@")[0],
                "credits": account.credits
            }
        }
