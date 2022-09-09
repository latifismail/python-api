from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models
from .database import engine, get_db
from .schemas import PostCreate, PostUpdate, PostResponse


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/latest", response_model=PostResponse)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).limit(1).first()
    return post

@app.get("/posts/{id}", response_model=PostResponse)
def get_post(id, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    return post

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
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

@app.put("/posts/{id}")
def update_post(id, payload: PostUpdate, db: Session = Depends(get_db), response_model=PostResponse):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return post.first()
