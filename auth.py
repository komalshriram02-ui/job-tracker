import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

import models
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY missing in .env file")

ALGORITHM = "HS256"
COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def set_login_cookie(response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=12 * 3600,
        path="/",
    )


def clear_login_cookie(response):
    response.delete_cookie(key=COOKIE_NAME, path="/")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    token = token or request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user