from datetime import date
from typing import List

from fastapi import FastAPI, Depends
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
def list_applications(db: Session = Depends(get_db)):
    return db.query(models.Application).all()