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