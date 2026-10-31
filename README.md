# Job Application Tracker

A full-stack web app to track job applications. Built with Python, FastAPI and SQLAlchemy.

## Features

- User registration and login with JWT authentication
- Passwords hashed with Argon2 (never stored as plain text)
- Input validation (clean usernames, strong passwords)
- Brute-force protection: login locks for 5 minutes after 5 failed attempts
- Secret key kept in a `.env` file, not in the code
- Full CRUD for job applications (add, view, update status, delete)
- Each user sees only their own applications
- Search and filter by status (API)
- Stats dashboard: total applications and count per status
- Simple web dashboard (HTML, CSS, JavaScript)

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite
- **Auth:** JWT (PyJWT), Argon2 (pwdlib)
- **Frontend:** HTML, CSS, JavaScript

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

Interactive API docs are available at `/docs` when the server is running.

## How to Run

1. Clone the repository and open the folder.

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the packages:
   ```
   pip install fastapi uvicorn sqlalchemy "pwdlib[argon2]" pyjwt python-multipart python-dotenv
   ```

4. Create a `.env` file in the project folder with a random secret key:
   ```
   SECRET_KEY=your_random_secret_key
   ```
   You can generate one with:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Start the server:
   ```
   uvicorn main:app --reload
   ```

6. Open `http://127.0.0.1:8000` in your browser.

## Author

Komal Shriram