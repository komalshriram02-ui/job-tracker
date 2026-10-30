from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker")


@app.get("/")
def home():
    return {"message": "Job Tracker is running"}


@app.post("/applications", response_model=schemas.ApplicationOut)
def create_application(data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    new_app = models.Application(
        company=data.company,
        role=data.role,
        status=data.status,
        applied_date=data.applied_date or date.today(),
        notes=data.notes,
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
):
    query = db.query(models.Application)

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
def update_application(app_id: int, data: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@app.delete("/applications/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()
    return {"message": "Application deleted"}