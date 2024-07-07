from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
