from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    published: bool

class PostResponse(PostBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
