from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.utils.crypto import encrypt_value, decrypt_value

class UserService:

    def create_user(self, db: Session, dto):
        existing = db.query(User).filter(User.username == dto.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(
            username=dto.username,
            email=dto.email,
            password_hash=hash_password(dto.password),

            groww_api_key=encrypt_value(dto.groww_api_key),
            groww_secret_key=encrypt_value(dto.groww_secret_key)
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, dto):
        user = db.query(User).filter(User.username == dto.username).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(dto.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="User disabled")

        return user

    def get_profile(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active
        }

    def get_decrypted_keys(self, user: User):
        return {
            "api_key": decrypt_value(user.groww_api_key),
            "secret_key": decrypt_value(user.groww_secret_key)
        }
