# Rental Platform API

A backend REST API for a housing rental platform, built with Django and Django REST Framework. Supports listing management, search and filtering, JWT authentication, bookings with status workflow, and reviews.

## Tech Stack

- **Backend:** Django 4.2, Django REST Framework
- **Database:** MySQL 8.0
- **Auth:** JWT (djangorestframework-simplejwt), login via email
- **API docs:** drf-spectacular (Swagger / ReDoc)
- **Containerization:** Docker, Docker Compose
- **Deployment:** AWS EC2

## Features

- **Listings:** create, edit, delete, toggle active/inactive; search by title/description; filter by price range, rooms range, city, property type; sort by price or date
- **Auth:** registration, login via email + password (JWT), password change
- **Roles:** tenant (browse/book) and landlord (manage own listings) — a user can hold either role
- **Bookings:** create, confirm/reject (landlord), cancel (tenant, before start date), status history logged
- **Reviews:** leave a review only for a confirmed booking you made; one review per booking

## Project Structure

```
config/       # settings, root urls
accounts/     # User model, auth, registration
listings/     # Listing model, search/filters
bookings/     # Booking model, status workflow, signals/logging
reviews/      # Review model
```

## Running Locally (without Docker)

Requires Python 3.9+ and a running MySQL server.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DB_HOST=127.0.0.1 and your local MySQL credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

App: http://127.0.0.1:8000/
Swagger: http://127.0.0.1:8000/api/docs/
Admin: http://127.0.0.1:8000/admin/

## Running with Docker

Requires Docker and Docker Compose.

```bash
cp .env.example .env
# edit .env: DB_HOST=db, set a real SECRET_KEY and DB_PASSWORD

docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

`docker-compose.override.yml` (local-only, not committed) additionally exposes MySQL on port 3306 for external tools (e.g. MySQL Workbench).


## API Overview

All endpoints are prefixed with `/api/v1/`.

| Endpoint | Method | Description |
|---|---|---|
| `/accounts/register/` | POST | Register a new user |
| `/auth/token/` | POST | Login (email + password) |
| `/auth/token/refresh/` | POST | Refresh access token |
| `/auth/token/blacklist/` | POST | Logout (blacklist refresh token) |
| `/accounts/me/` | GET, PATCH | View/edit own profile |
| `/accounts/me/change-password/` | POST | Change password |
| `/listings/` | GET, POST | List/create listings |
| `/listings/{id}/` | GET, PATCH, DELETE | Listing detail/edit/delete |
| `/bookings/` | GET, POST | List/create bookings |
| `/bookings/{id}/confirm/` | POST | Confirm booking (landlord) |
| `/bookings/{id}/reject/` | POST | Reject booking (landlord) |
| `/bookings/{id}/cancel/` | POST | Cancel booking (tenant) |
| `/reviews/` | GET, POST | List/create reviews |
| `/reviews/{id}/` | PATCH, DELETE | Edit/delete own review |

Full interactive documentation: `/api/docs/` (Swagger UI) or `/api/redoc/`.

### Listing filters (query params)

`price_min`, `price_max`, `rooms_min`, `rooms_max`, `city`, `property_type`, `search`, `ordering` (`price`, `-price`, `created_at`, `-created_at`)

### Booking filters (query params)

`status`, `start_date_from`, `start_date_to`, `is_completed`

## Environment Variables

See `.env.example` for the full list. Key ones:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key — generate a new one for production |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts/IPs |
| `DB_HOST` | `127.0.0.1` locally, `db` when using Docker Compose |

## Deployment

Deployed on an AWS EC2 instance (Amazon Linux) running Docker Compose, with a static Elastic IP. See `Dockerfile`, `docker-compose.yml`, and `entrypoint.sh` for the container setup — the entrypoint waits for MySQL to become available, runs migrations, collects static files (served via WhiteNoise), then starts Gunicorn.