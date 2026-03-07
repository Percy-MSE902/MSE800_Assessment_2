from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import pyotp
import qrcode
import io
import base64

from database import get_db
from models.user import UserModel
from schemas.login import LoginRequest, Token, UserInfo
from core.security import create_access_token

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    enable_2fa: bool = False


class TwoFactorResponse(BaseModel):
    requires_2fa: bool
    temp_token: Optional[str] = None
    qr_code: Optional[str] = None
    message: Optional[str] = None


@auth_router.post("/register", response_model=TwoFactorResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = UserModel(
        username=request.username,
        password=request.password,
        full_name=request.full_name or request.username,
        email=request.email,
        role='guest',
        status=1
    )
    user.set_password(request.password)
    
    if request.enable_2fa:
        totp_secret = pyotp.random_base32()
        user.totp_secret = totp_secret
        user.is_2fa_enabled = 1
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        totp = pyotp.TOTP(totp_secret)
        provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Housekeeping")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return TwoFactorResponse(
            requires_2fa=True,
            qr_code=f"data:image/png;base64,{qr_code_base64}",
            message="Please scan the QR code with your authenticator app and verify with a code"
        )
    else:
        db.add(user)
        db.commit()
        
        token = create_access_token(subject=user.username)
        return TwoFactorResponse(
            requires_2fa=False,
            temp_token=token,
            message="Registration successful"
        )


@auth_router.post("/verify-2fa")
def verify_2fa(
    username: str,
    code: str,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.totp_secret or not user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled for this user")
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=401, detail="Invalid verification code")
    
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token)
def login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.password.startswith('$2b$'):
        if not user.verify_password(data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    else:
        if user.password != data.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.is_2fa_enabled and user.totp_secret:
        return Token(
            access_token=create_access_token(subject=f"{user.username}_2fa"),
            token_type="bearer",
            requires_2fa=True
        )
    
    token = create_access_token(subject=user.username)
    return Token(
        access_token=token,
        token_type="bearer",
        user_info=UserInfo(
            id=user.id,
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            email=user.email
        )
    )


class LoginRequestJSON(BaseModel):
    username: str
    password: str


@auth_router.post("/login/json", response_model=Token)
def login_json(
    request: LoginRequestJSON,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.password.startswith('$2b$'):
        if not user.verify_password(request.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    else:
        if user.password != request.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.is_2fa_enabled and user.totp_secret:
        return Token(
            access_token=create_access_token(subject=f"{user.username}_2fa"),
            token_type="bearer",
            requires_2fa=True
        )
    
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}
    
    if user.is_2fa_enabled and user.totp_secret:
        temp_token = create_access_token(subject=f"{user.username}_2fa")
        return Token(
            access_token=temp_token,
            token_type="bearer",
            requires_2fa=True
        )
    
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}


class LoginWith2FARequest(BaseModel):
    username: str
    password: str
    code: str


@auth_router.post("/login-with-2fa")
def login_with_2fa(
    request: LoginWith2FARequest,
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.password.startswith('$2b$'):
        if not user.verify_password(request.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    else:
        if user.password != request.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if user.is_2fa_enabled and user.totp_secret:
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(request.code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}
