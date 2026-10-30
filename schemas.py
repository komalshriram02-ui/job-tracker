
from datetime import date
from typing import Optional
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: str = "Applied"
    applied_date: Optional[date] = None
    notes: str = ""


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None


class ApplicationOut(ApplicationCreate):
    id: int

    model_config = {"from_attributes": True}
