from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import UserModel
from schemas.login import LoginRequest, Token
from core.security import create_access_token

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

@auth_router.post("/login", response_model=Token)
def login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # For plaintext passwords in DB, or bcrypt
    if user.password.startswith('$2b$'):
        if not user.verify_password(data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    else:
        # Plaintext comparison for initial data
        if user.password != data.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}
