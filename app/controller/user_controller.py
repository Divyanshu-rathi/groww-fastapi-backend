from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.service.user_service import UserService
from app.dto.user_dto import CreateUserDTO, LoginUserDTO
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User"])
service = UserService()

@router.post("/create")
def create_user(
    request: CreateUserDTO,
    db: Session = Depends(get_db)
):
    user = service.create_user(db, request)
    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username
    }

@router.post("/login")
def login(
    request: LoginUserDTO,
    db: Session = Depends(get_db)
):
    user = service.authenticate(db, request)
    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username
    }

@router.get("/profile")
def get_profile(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    return service.get_profile(db, x_user_id)
