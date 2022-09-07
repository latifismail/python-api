from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from psycopg2.extras import RealDictCursor
import psycopg2

from app import config

app = FastAPI()

try:
    conn = psycopg2.connect(
        host=config.HOST, database=config.DB, user=config.USER, password=config.PASSWORD,
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    print(f"Connected to {config.DB} on {config.HOST}")

except Exception as error:
    print("Failed to connect to database")
    print(f"Error: {error}")

class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data": posts}

@app.get("/posts/latest")
def get_latest_post():
    cursor.execute(
        """
        SELECT * FROM posts
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    post = cursor.fetchone()
    return {"data": post}

@app.get("/posts/{id}")
def get_post(id):
    cursor.execute(
        """
        SELECT * FROM posts
        where id = %s
        """, (id)
    )
    post = cursor.fetchone()
    if post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: Post, response: Response):
    cursor.execute(
        """
        INSERT INTO posts (title, content, published, rating)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """, (payload.title, payload.content, payload.published, payload.rating)
    )
    post = cursor.fetchone()
    conn.commit()

    return {
        "message": "Post created successfully",
        "data": post
    }

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id):
    cursor.execute(
        """
        DELETE FROM posts
        WHERE id = %s
        """, (id)
    )
    conn.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id, payload: Post):
    cursor.execute(
        """
        UPDATE posts
        SET title = %s, content = %s, published = %s, rating = %s
        WHERE id = %s
        RETURNING *
        """, (payload.title, payload.content, payload.published, payload.rating, id)
    )
    updated_post = cursor.fetchone()
    conn.commit()
    
    return {
        "message": "Post updated successfully",
        "data": updated_post
    }
