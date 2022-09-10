from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

from . import models
from .database import engine, get_db
from . import schemas


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def bcrypt_hash(password: str):
    result = password_context.hash(password)
    return result

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).limit(1).first()
    return post

@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_post(id, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db)):
    post = models.Post(**payload.dict())

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@app.delete("/posts/{id}")
def delete_post(id, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_post(id, payload: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    try:

        hashed_password =  bcrypt_hash(payload.password)
        payload.password = hashed_password

        user = models.User(**payload.dict())

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User or Email already exist")

@app.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist")

    return user
