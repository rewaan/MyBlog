from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str]
    video_url: Optional[str]
    created_at: datetime
    owner_id: int
    class Config:
        orm_mode = True
