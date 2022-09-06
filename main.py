from fastapi import FastAPI
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

def find_post(id):
    result = next((post for post in posts if post["id"] == id), None)
    return result

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
    post = find_post(id)
    if post == None:
        return {"message": "Post not found"}

    return {"data": post}

@app.post("/posts")
def create_posts(payload: Post):
    post = payload.dict()
    post['id'] = str(uuid.uuid4())
    posts.append(post)

    return {
        "message": "success",
        "data": post
    }
