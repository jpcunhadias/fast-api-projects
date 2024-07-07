from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user  # Ensure this import is correct

router = APIRouter()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


# Pydantic model for request validation
class TodoRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=100)
    priority: int = Field(..., ge=1, le=5)
    completed: bool = False


# Root endpoint to get all todos
@router.get("/")
async def get_todos(db: Session = db_dependency):
    return db.query(Todos).all()


# Get a todo by ID
@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(todo_id: int = Path(gt=0), db: Session = db_dependency):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


# Create a new todo
@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, db: Session = db_dependency, user: dict = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = Todos(**todo.dict(), user_id=user.get("user_id"))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo: TodoRequest, todo_id: int = Path(gt=0), db: Session = db_dependency):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.completed = todo.completed

    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(todo_id: int = Path(gt=0), db: Session = db_dependency):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_model)
    db.commit()
    return None
