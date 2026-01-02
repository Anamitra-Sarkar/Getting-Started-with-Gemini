from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from .db import engine
from .models import User
from .auth import get_password_hash, verify_password, create_access_token
from typing import Dict

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: Dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")
    with Session(engine) as session:
        exists = session.exec(select(User).where(User.email == email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="User exists")
        user = User(email=email, hashed_password=get_password_hash(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}


@router.post("/token")
def token(form_data: Dict):
    # expects {"username":...,"password":...}
    username = form_data.get("username")
    password = form_data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == username)).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
