# SmartVote Backend — Django REST Framework

Backend API for **USTP SmartVote**, a face-verified student council election system.

## Tech Stack
- Python 3.x · Django 4+ · Django REST Framework · SimpleJWT · PostgreSQL

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/<you>/smartvote-backend.git
cd smartvote-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the database in smartvote/settings.py
#    Set NAME, USER, PASSWORD for your local PostgreSQL

# 5. Create the database in psql
#    CREATE DATABASE smartvote_db;

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create a superuser (admin)
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register new voter | Public |
| POST | `/api/auth/login/` | Login → JWT tokens | Public |
| POST | `/api/auth/token/refresh/` | Refresh access token | Public |
| GET/PUT | `/api/auth/profile/` | View/edit own profile | Student |
| GET | `/api/candidates/` | List all candidates | Auth |
| POST | `/api/candidates/` | Add candidate | Admin |
| GET/PUT/DELETE | `/api/candidates/<id>/` | Candidate detail | Auth/Admin |
| POST | `/api/vote/` | Cast a vote | Student |
| GET | `/api/vote/my/` | My vote history | Student |
| GET | `/api/results/` | Election results tally | Public |
| GET | `/api/dashboard/` | Admin stats & tally | Admin |
| GET | `/api/voter-log/` | Voter activity log | Admin |
| GET/POST/PUT | `/api/election-settings/` | Manage election settings | Admin |

## Testing with httpie

```bash
# Register
http POST http://127.0.0.1:8000/api/auth/register/ \
    student_id="2024-00123" email="juan@gmail.com" \
    full_name="Juan Dela Cruz" password="pass1234"

# Login
http POST http://127.0.0.1:8000/api/auth/login/ \
    student_id="2024-00123" password="pass1234"

# List candidates (with token)
http GET http://127.0.0.1:8000/api/candidates/ \
    "Authorization: Bearer <token>"

# Cast a vote
http POST http://127.0.0.1:8000/api/vote/ \
    "Authorization: Bearer <token>" candidate=1

# Results
http GET http://127.0.0.1:8000/api/results/
```
