# Job Application Tracker

A full-stack web app to track job applications, with AI-powered job description reading. Built with Python, FastAPI and SQLAlchemy.

**Live demo:** https://job-tracker-k8ob.onrender.com

_Note: hosted on a free plan, so the first load may take about 50 seconds._

## Features

- User registration and login with JWT authentication
- Passwords hashed with Argon2 (never stored as plain text)
- Input validation (clean usernames, strong passwords)
- Brute-force protection: login locks for 5 minutes after 5 failed attempts
- Secrets (secret key, database URL, API key) kept in environment variables, not in the code
- Full CRUD for job applications (add, view, update status, delete)
- Each user sees only their own applications
- Search and filter by company, role or status
- Stats dashboard: total applications and count per status
- AI auto-fill: paste a job description and Google Gemini fills in the company, role and key skills
- AI cover letter generator: one click writes a short, tailored cover letter for any application
- Responsive single-page UI (HTML, CSS, JavaScript)

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (Neon), SQLite for local development
- **Auth:** JWT (PyJWT), Argon2 (pwdlib)
- **AI:** Google Gemini API (google-genai)
- **Frontend:** HTML, CSS, JavaScript
- **Hosting:** Render

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create a new user |
| POST | /auth/login | Login and get a token |
| POST | /applications | Add an application |
| GET | /applications | List applications (optional `status` and `q` filters) |
| PUT | /applications/{id} | Update an application |
| DELETE | /applications/{id} | Delete an application |
| GET | /stats | Application counts by status |
| POST | /ai/extract | Extract company, role and skills from a job description |
| POST | /ai/cover-letter | Generate a cover letter for an application |
Interactive API docs are available at `/docs` when the server is running.

## How to Run Locally

1. Clone the repository and open the folder.

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder:
   ```
   SECRET_KEY=your_random_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=your_postgres_url   # optional, SQLite is used if missing
   ```
   Generate a secret key with:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Get a free Gemini API key from Google AI Studio.

5. Start the server:
   ```
   uvicorn main:app --reload
   ```

6. Open `http://127.0.0.1:8000` in your browser.

## Author

Komal Shriram