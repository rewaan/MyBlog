import os
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Response, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from . import crud
from .utils import env_bool
import bleach

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret_jwt_key_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ALLOW_SECURE_COOKIE = env_bool("ENV_ALLOW_SECURE_COOKIE", False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # for dependencies

def get_password_hash(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _jwt(payload: dict, minutes: int | None = None, days: int | None = None, typ: str = "access") -> str:
    to_encode = payload.copy()
    if minutes is not None:
        exp = datetime.utcnow() + timedelta(minutes=minutes)
    elif days is not None:
        exp = datetime.utcnow() + timedelta(days=days)
    else:
        exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": exp, "type": typ})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_access_token(sub: str) -> str:
    return _jwt({"sub": sub}, minutes=ACCESS_TOKEN_EXPIRE_MINUTES, typ="access")

def create_refresh_token(sub: str) -> str:
    return _jwt({"sub": sub}, days=REFRESH_TOKEN_EXPIRE_DAYS, typ="refresh")

def authenticate_user(db: Session, username: str, password: str):
    u = crud.get_user_by_username(db, username)
    if not u or not verify_password(password, u.hashed_password):
        return None
    return u

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise cred_exc
        username: str | None = payload.get("sub")
        if not username:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = crud.get_user_by_username(db, username)
    if not user:
        raise cred_exc
    return user

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=ALLOW_SECURE_COOKIE,   # prod: true + HTTPS
        samesite="strict",            # rozważ "none" przy innej domenie frontu
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

# prosta sanitizacja treści HTML
def sanitize_html(html: str) -> str:
    allowed_tags = sorted(set(bleach.sanitizer.ALLOWED_TAGS).union({
        "p","br","div","span","h1","h2","h3","h4","h5","h6",
        "img","strong","em","ul","ol","li","blockquote","pre","code","a"}))
    allowed_attrs = {
        "a": ["href","title","target","rel"],
        "img": ["src","alt","title","width","height"],
        "*": ["style"],
    }
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
