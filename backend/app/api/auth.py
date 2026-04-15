from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import User
from app.services.auth_service import hash_password, verify_password, create_token

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: LoginRequest, db: Session = Depends(get_db)):
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"status": "ok"}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        return {"error": "invalid credentials"}

    token = create_token(str(user.id))
    return {"access_token": token}