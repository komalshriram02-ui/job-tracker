
import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("username")
    @classmethod
    def clean_username(cls, v):
        v = v.strip().lower()
        if not re.fullmatch(r"[a-z0-9_]+", v):
            raise ValueError("Only letters, numbers and underscore allowed")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if not (re.search(r"[A-Za-z]", v) and re.search(r"\d", v)):
            raise ValueError("Password must have both letters and numbers")
        return v

class JobDescriptionIn(BaseModel):
    text: str = Field(min_length=20, max_length=8000)


class CoverLetterIn(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    skills: str = Field(default="", max_length=300)
    about_me: str = Field(default="", max_length=500)    
