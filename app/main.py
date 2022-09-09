from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class Post(BaseModel):
    title: str
    content: str
    published: bool = False


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/posts/latest")
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post).order_by(models.Post.created_at.desc()).limit(1).first()
    return {"data": post}

@app.get("/posts/{id}")
def get_post(id, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: Post, db: Session = Depends(get_db)):
    post = models.Post(**payload.dict())

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "message": "Post created successfully",
        "data": post
    }

@app.delete("/posts/{id}")
def delete_post(id, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id, payload: Post, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return {
        "message": "Post updated successfully",
        "data": post.first()
    }
