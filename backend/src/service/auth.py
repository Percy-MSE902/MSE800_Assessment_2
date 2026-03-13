import base64

from sqlalchemy.orm import Session

from model.user import UserModel
from core.security import create_access_token

import pyotp
import qrcode
import io


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, password: str, full_name: str = None, email: str = None, enable_2fa: bool = False):
        existing_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if existing_user:
            return {"error": "Username already exists", "status_code": 400}

        user = UserModel(
            username=username,
            password=password,
            full_name=full_name or username,
            email=email,
            role='guest',
            status=1
        )
        user.set_password(password)

        if enable_2fa:
            totp_secret = pyotp.random_base32()
            user.totp_secret = totp_secret
            user.is_2fa_enabled = 1

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            totp = pyotp.TOTP(totp_secret)
            provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Housekeeping")

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return {
                "requires_2fa": True,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "message": "Please scan the QR code with your authenticator app and verify with a code"
            }
        else:
            self.db.add(user)
            self.db.commit()

            token = create_access_token(subject=user.username)
            return {
                "requires_2fa": False,
                "temp_token": token,
                "message": "Registration successful"
            }

    def verify_2fa(self, username: str, code: str):
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "User not found", "status_code": 404}

        if not user.totp_secret or not user.is_2fa_enabled:
            return {"error": "2FA not enabled for this user", "status_code": 400}

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(code):
            return {"error": "Invalid verification code", "status_code": 401}

        token = create_access_token(subject=user.username)
        return {"access_token": token, "token_type": "bearer"}

    def login(self, username: str, password: str):
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.password.startswith('$2b$'):
            if not user.verify_password(password):
                return {"error": "Invalid credentials", "status_code": 401}
        else:
            if user.password != password:
                return {"error": "Invalid credentials", "status_code": 401}

        if user.is_2fa_enabled and user.totp_secret:
            return {
                "access_token": create_access_token(subject=f"{user.username}_2fa"),
                "token_type": "bearer",
                "requires_2fa": True
            }

        token = create_access_token(subject=user.username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name,
                "email": user.email
            }
        }

    def login_with_2fa(self, username: str, password: str, code: str):
        user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            return {"error": "Invalid credentials", "status_code": 401}

        if user.password.startswith('$2b$'):
            if not user.verify_password(password):
                return {"error": "Invalid credentials", "status_code": 401}
        else:
            if user.password != password:
                return {"error": "Invalid credentials", "status_code": 401}

        if user.is_2fa_enabled and user.totp_secret:
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(code):
                return {"error": "Invalid 2FA code", "status_code": 401}

        token = create_access_token(subject=user.username)
        return {"access_token": token, "token_type": "bearer"}
