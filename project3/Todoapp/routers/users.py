from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from database import SessionLocal
from .auth import get_current_user
from models import Users
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user_me(user: dict = user_dependency, db=Depends(db_dependency)):
    user = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(user_verification: UserVerification, db=Depends(db_dependency)):
    user = db.query(Users).filter(Users.username == user_verification.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(user_verification.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"message": "User verified successfully"}


@router.put("/update", status_code=status.HTTP_200_OK)
async def change_password(user_verification: UserVerification, user: dict = user_dependency, db=Depends(db_dependency), ):
    user = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(user_verification.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user.hashed_password = pwd_context.hash(user_verification.password)
    db.commit()
    return {"message": "Password updated successfully"}