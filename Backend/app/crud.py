from sqlalchemy.orm import Session
from . import models
from .auth import get_password_hash

def create_user(db: Session, username: str, password: str):
    user = models.User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_post(db: Session, *, title: str, content: str, owner_id: int, image_url: str | None, video_url: str | None):
    p = models.Post(title=title, content=content, owner_id=owner_id, image_url=image_url, video_url=video_url)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def get_posts(db: Session, limit: int = 100):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).limit(limit).all()
