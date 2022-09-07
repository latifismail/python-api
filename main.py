from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

posts = []

def find_post(id) -> tuple:
    for index, post in enumerate(posts):
        if post["id"] == id:
            return index, post
    return None, None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    return {"data": posts}

@app.get("/posts/latest")
def get_latest_post():
    post = posts[-1]
    return {"data": post}

@app.get("/posts/{id}")
def get_post(id):
    _, post = find_post(id)
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: Post, response: Response):
    post = payload.dict()
    post['id'] = str(uuid.uuid4())
    posts.append(post)

    return {
        "message": "success",
        "data": post
    }

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id):
    index, _ = find_post(id)
    if index == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    
    posts.pop(index)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
