import os
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from .database import Base, engine, get_db
from . import models, schemas, crud, auth, s3
from .utils import env_list

# DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API (Railway + Neon + R2)")

# CORS
FRONTEND_ORIGINS = env_list("FRONTEND_ORIGINS") or ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,   # ważne dla cookie refresh
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- AUTH ----
@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    u = crud.create_user(db, user.username, user.password)
    access = auth.create_access_token(u.username)
    refresh = auth.create_refresh_token(u.username)
    resp = JSONResponse({"access_token": access})
    auth.set_refresh_cookie(resp, refresh)
    return resp

@app.post("/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    u = auth.authenticate_user(db, payload.username, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access = auth.create_access_token(u.username)
    refresh = auth.create_refresh_token(u.username)
    resp = JSONResponse({"access_token": access})
    auth.set_refresh_cookie(resp, refresh)
    return resp

@app.post("/auth/refresh", response_model=schemas.Token)
def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET",""), algorithms=[os.getenv("JWT_ALGORITHM","HS256")])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"access_token": auth.create_access_token(sub)}

@app.post("/auth/logout")
def logout():
    # nadpisanie cookie i natychmiastowe wygaśnięcie
    resp = JSONResponse({"ok": True})
    resp.set_cookie("refresh_token", "", max_age=0, httponly=True, path="/")
    return resp

# ---- POSTS ----
@app.get("/posts", response_model=List[schemas.PostOut])
def list_posts(db: Session = Depends(get_db)):
    return crud.get_posts(db)

@app.post("/posts", response_model=schemas.PostOut)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    clean_html = auth.sanitize_html(content)

    image_url = None
    if image:
        image_url = s3.upload_bytes(await image.read(), image.filename)

    video_url = None
    if video:
        video_url = s3.upload_bytes(await video.read(), video.filename)

    return crud.create_post(
        db,
        title=title,
        content=clean_html,
        owner_id=current_user.id,
        image_url=image_url,
        video_url=video_url,
    )
