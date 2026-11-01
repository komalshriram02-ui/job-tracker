import csv
import io

from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

import auth
import ai
import rate_limit
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/applications", response_model=schemas.ApplicationOut)
def create_application(
    data: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    new_app = models.Application(
        company=data.company,
        role=data.role,
        status=data.status,
        applied_date=data.applied_date or date.today(),
        notes=data.notes,
        owner_id=user.id,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


@app.get("/applications", response_model=List[schemas.ApplicationOut])
def list_applications(
    status: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Application).filter(models.Application.owner_id == user.id)

    if status:
        query = query.filter(models.Application.status == status)

    if q:
        search = f"%{q}%"
        query = query.filter(
            models.Application.company.ilike(search)
            | models.Application.role.ilike(search)
        )

    return query.all()


@app.put("/applications/{app_id}", response_model=schemas.ApplicationOut)
def update_application(
    app_id: int,
    data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    application = (
        db.query(models.Application)
        .filter(models.Application.id == app_id, models.Application.owner_id == user.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@app.delete("/applications/{app_id}")
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    application = (
        db.query(models.Application)
        .filter(models.Application.id == app_id, models.Application.owner_id == user.id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()
    return {"message": "Application deleted"}


@app.post("/auth/register", status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=data.username,
        hashed_password=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    return {"message": "User registered"}


@app.post("/auth/login")
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = form.username.strip().lower()
    rate_limit.check_locked(username)

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        rate_limit.record_failure(username)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    rate_limit.reset(username)
    token = auth.create_token(user.username)
    auth.set_login_cookie(response, token)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/logout")
def logout(response: Response):
    auth.clear_login_cookie(response)
    return {"message": "Logged out"}


@app.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    rows = (
        db.query(models.Application.status, func.count(models.Application.id))
        .filter(models.Application.owner_id == user.id)
        .group_by(models.Application.status)
        .all()
    )
    by_status = {status: count for status, count in rows}
    return {"total": sum(by_status.values()), "by_status": by_status}


def ai_user(user: models.User = Depends(auth.get_current_user)):
    rate_limit.check_ai_limit(user.id)
    return user


@app.post("/ai/extract")
def ai_extract(data: schemas.JobDescriptionIn, user: models.User = Depends(ai_user)):
    return ai.extract_job_details(data.text)


@app.post("/ai/cover-letter")
def ai_cover_letter(data: schemas.CoverLetterIn, user: models.User = Depends(ai_user)):
    letter = ai.write_cover_letter(data.company, data.role, data.skills, data.about_me)
    return {"cover_letter": letter}


@app.post("/ai/interview-questions")
def ai_interview_questions(data: schemas.InterviewIn, user: models.User = Depends(ai_user)):
    return ai.interview_questions(data.company, data.role, data.skills)


@app.post("/ai/match")
def ai_match(data: schemas.MatchIn, user: models.User = Depends(ai_user)):
    return ai.match_resume(data.resume, data.job_description)


def _safe_cell(value) -> str:
    # Stops spreadsheet formula injection (cells starting with = + - @)
    text = "" if value is None else str(value)
    if text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


@app.get("/applications/export")
def export_applications(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    apps = (
        db.query(models.Application)
        .filter(models.Application.owner_id == user.id)
        .order_by(models.Application.applied_date.desc())
        .all()
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Company", "Role", "Status", "Applied Date", "Notes"])
    for a in apps:
        writer.writerow([
            _safe_cell(a.company),
            _safe_cell(a.role),
            _safe_cell(a.status),
            a.applied_date,
            _safe_cell(a.notes),
        ])
    return Response(
        content="\ufeff" + buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )    