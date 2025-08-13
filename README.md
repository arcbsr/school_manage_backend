# School Management API (Django + DRF)

A modular Django REST API for a school management system. Includes JWT auth, API key support, RBAC, OpenAPI docs, and core school structure models (Branch, Shift, Class, Section, Subject).

## Prerequisites
- Python 3.9+
- pip

Optional (recommended):
- Virtualenv/venv

## Quick Start

```bash
# 1) Clone and enter project
cd SchoolManagement

# 2) (Optional) Create and activate virtualenv
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create .env file in Backend/config scope (project root is also fine)
# See example below

# 5) Run migrations
python Backend/manage.py migrate

# 6) Seed default data (admin + branch/classes/sections/shifts/subjects)
python Backend/manage.py seed_defaults

# 7) Start server
python Backend/manage.py runserver
```

Open:
- Swagger UI: http://127.0.0.1:8000/api/docs/
- Schema (OpenAPI): http://127.0.0.1:8000/api/schema/
- Admin: http://127.0.0.1:8000/admin/

## Environment (.env)
Create a `.env` file with at least the following keys. The app looks for these via python-decouple.

```env
# Security / Django
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
TIME_ZONE=UTC

# Auth
# Comma-separated list of API keys allowed to access the API (e.g., service-to-service)
API_KEYS=your-dev-api-key

# Default admin user (used by seeder and startup hook)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe123!
# Optional: override default username; otherwise uses email local-part
# ADMIN_USERNAME=admin

# Optional Postgres (if omitted, SQLite is used automatically)
# DB_NAME=school_db
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# CORS (optional)
# CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Notes:
- If `DB_NAME` is missing, the app uses SQLite at `Backend/db.sqlite3`.
- If `DB_NAME` is present, the app uses Postgres with the given credentials.

## Authentication
The API requires authentication by default (global `IsAuthenticated`). Two methods are supported:

- API Key header (preferred for services):
  - Header: `X-API-Key: <key>`
  - Keys are read from `API_KEYS` in `.env`.

- JWT (for users/admins):
  - Login: `POST /api/auth/login` with `{ "username": "<user>", "password": "<pass>" }`
  - Refresh: `POST /api/auth/refresh`
  - Logout (blacklist refresh): `POST /api/auth/logout` with `{ "refresh": "<token>" }`
  - Use header: `Authorization: Bearer <access_token>`

RBAC:
- Write operations require a superuser or a user with `manage_school` permission (via `django-role-permissions`).
- Read operations (GET/HEAD/OPTIONS) require authentication but are generally allowed to all authenticated users.

## Core Endpoints
All endpoints are prefixed with `/api/`.

- Auth
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `POST /api/auth/logout`

- School structure
  - Branches: `GET/POST /api/branches/`, `GET/PUT/PATCH/DELETE /api/branches/{id}/`
  - Shifts: `GET/POST /api/shifts/`, `GET/PUT/PATCH/DELETE /api/shifts/{id}/`
  - Classes: `GET/POST /api/classes/`, `GET/PUT/PATCH/DELETE /api/classes/{id}/`
  - Sections: `GET/POST /api/sections/`, `GET/PUT/PATCH/DELETE /api/sections/{id}/`
  - Subjects: `GET/POST /api/subjects/`, `GET/PUT/PATCH/DELETE /api/subjects/{id}/`

- Reports
  - Combined active data: `GET /api/reports/branch_data`
    - Response includes arrays: `classes`, `sections`, `shifts`, `sessions`

- Health
  - `GET /api/health/`
  - DB health: `GET /api/health/db/`

## Seeding
The seeder creates:
- Superuser from `.env` (`ADMIN_EMAIL`/`ADMIN_PASSWORD`; username defaults to email local-part)
- Branch `Khilgaon`
- Shifts `Day` and `Afternoon`
- Classes `Play, Nursery, KG, One–Ten`
- Sections `A`, `B` for each class
- Subjects `Math, English, Science`

Run:
```bash
python Backend/manage.py seed_defaults
```

## Curl Examples

API key auth:
```bash
curl -H "X-API-Key: your-dev-api-key" http://127.0.0.1:8000/api/branches/
```

JWT auth:
```bash
# Login to get tokens
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"ChangeMe123!"}'

# Use access token
curl -H "Authorization: Bearer <access>" http://127.0.0.1:8000/api/branches/
```

## Development Notes
- OpenAPI/Swagger provided by `drf-spectacular` at `/api/docs/` and `/api/schema/`.
- RBAC provided by `django-role-permissions`.
- Default permission is `IsAuthenticated`. Override cautiously with `AllowAny` only for public endpoints.
- To update schema file on disk (optional):
  ```bash
  python Backend/manage.py spectacular --file schema.yaml
  ```

## Switching to Postgres (optional)
1) Install driver:
```bash
pip install psycopg2-binary
```
2) Set DB env vars in `.env` (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
3) Run migrations:
```bash
python Backend/manage.py migrate
```

## Project Structure
- `Backend/config/` – Django project config
- `Backend/core/` – App with models, views, auth, permissions, management commands
- `requirements.txt` – Python dependencies

## Troubleshooting
- 403 errors on writes: ensure you’re superuser or have `manage_school` permission; auth is required for all endpoints.
- Schema errors in Swagger: ensure server is running and migrations are applied.
