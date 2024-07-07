from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Todos, Users
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db: Session = db_dependency, user: dict = user_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_models = db.query(Todos).all()
    return todo_models

@router.get("/users/all", status_code=status.HTTP_200_OK)
async def get_all_users(db: Session = db_dependency, user: dict = user_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_models = db.query(Users).all()
    return user_models

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(todo_id: int = Path(gt=0), db: Session = db_dependency, user: dict = user_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_model)
    db.commit()
    return {"message": "Todo deleted successfully"}
