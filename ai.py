import json
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class JobInfo(BaseModel):
    company: str
    role: str
    notes: str


def extract_job_details(job_description: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI is not configured")

    client = genai.Client(api_key=api_key)
    prompt = (
        "Read this job description and extract: the company name, the job role/title, "
        "and a short note (max 25 words) listing the key skills required. "
        "If the company is not mentioned, use an empty string.\n\n"
        "Job description:\n" + job_description[:6000]
    )
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobInfo,
            ),
        )
        return json.loads(response.text)
    except Exception:
        raise HTTPException(status_code=502, detail="AI service error, try again")


def write_cover_letter(company: str, role: str, skills: str, about_me: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI is not configured")

    client = genai.Client(api_key=api_key)
    prompt = (
        "Write a short, professional cover letter (maximum 180 words) for a fresher "
        "applying for the job below. Use a polite and confident tone. Do not use "
        "placeholders like [Your Name]. If a candidate name is given, sign off with it.\n\n"
        f"Company: {company[:100]}\n"
        f"Role: {role[:100]}\n"
        f"Key skills required: {skills[:300]}\n"
        f"About the candidate: {about_me[:500]}"
    )
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception:
        raise HTTPException(status_code=502, detail="AI service error, try again")


class InterviewQuestion(BaseModel):
    question: str
    tip: str


class InterviewPrep(BaseModel):
    questions: list[InterviewQuestion]


def interview_questions(company: str, role: str, skills: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI is not configured")

    client = genai.Client(api_key=api_key)
    prompt = (
        "Give 6 likely interview questions for a fresher applying for the job below: "
        "4 technical questions and 2 HR questions. For each question, give a one-line "
        "tip on how to answer it well.\n\n"
        f"Company: {company[:100]}\n"
        f"Role: {role[:100]}\n"
        f"Key skills required: {skills[:300]}"
    )
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InterviewPrep,
            ),
        )
        return json.loads(response.text)
    except Exception:
        raise HTTPException(status_code=502, detail="AI service error, try again")        

