# AttendEase — College Event Attendance Management System

[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-Supabase_PostgreSQL-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![Auth](https://img.shields.io/badge/Auth-Supabase_Auth-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

**AttendEase** is an enterprise-grade Django web application designed to streamline and automate student attendance requests for college events. It features a multi-tiered approval hierarchy, role-based dashboards, Supabase cloud database & authentication integration, and Excel export capabilities.

---

## Key Features

- **Multi-Tier Approval Hierarchy**: Seamless progression of requests from students to event coordinators and class teachers.
- **Supabase Cloud Integration**: Native PostgreSQL database storage and Supabase Auth backend synchronization.
- **Role-Based Access Control**: Tailored dashboards and permissions for **Students**, **Event Coordinators**, and **Class Teachers**.
- **Dual Event Types**: Support for coordinator-hosted college events and external open events.
- **Excel Report Generation**: Class teachers can export real-time attendance logs directly to `.xlsx`.
- **Responsive Glassmorphic UI**: Polished, modern design system with sidebar navigation, stat counters, and flash messages.

---

## Roles & Permissions

| Role | Responsibilities & Capabilities |
| :--- | :--- |
| **Student** | Submit attendance requests for internal or open (external) events; track approval statuses in real-time. |
| **Event Coordinator** | Create and manage events; review, approve, or reject attendance requests for their assigned events. |
| **Class Teacher** | Final approval/rejection authority; mark verified attendance; export class attendance data to Excel. |
| **Admin** | Full system administration via the Django Admin panel at `/admin/`. |

---

## Approval Workflow

```text
                  Student Submits Request
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [Coordinator Event]                  [Open Event]
            │                                 │
            ▼                                 │
Coordinator Reviews (Approve/Reject)          │
            │                                 │
            └───► Approved ◄──────────────────┘
                     │
                     ▼
         Teacher Reviews (Approve/Reject)
                     │
                     ▼
         Teacher Marks Attended (✓)
                     │
                     ▼
          Export Attendance to Excel
```

*Note: Open (external) events skip the coordinator phase and route directly to the class teacher.*

---

## Quick Start Guide

### 1. Clone & Setup Environment

```bash
git clone https://github.com/yuvraj-044/AttendEase.git
cd AttendEase

# Create and activate virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate
```

### 2. Configure Environment Variables

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your Supabase credentials:

```env
# Django
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=True

# Supabase Database (PostgreSQL)
# Found in Supabase Dashboard → Settings → Database
SUPABASE_DB_HOST=db.yourprojectref.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_actual_db_password

# Supabase API
# Found in Supabase Dashboard → Settings → API
SUPABASE_URL=https://yourprojectref.supabase.co
SUPABASE_ANON_KEY=your_actual_anon_key
```

> **Connection Note:** If connecting from an IPv4-only network, use the **Transaction Pooler** host and port (`6543` or `5432`) provided in your Supabase Database Settings.

### 3. Install Dependencies

```bash
pip3 install -r requirements/local.txt
```

### 4. Apply Database Migrations

Run migrations to create all required schema tables in Supabase PostgreSQL:

```bash
python3 manage.py migrate
```

### 5. Create an Administrator Superuser

```bash
python3 manage.py createsuperuser
```

### 6. Start the Development Server

```bash
# Run using the helper script
./run.sh

# Or start directly with Django
python3 manage.py runserver
```

Open your browser and navigate to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.

---

## Project Structure

The project adheres to a modular, scalable architecture separating configuration, apps, static assets, and templates:

```text
AttendEase/
├── .env                        # Local environment secrets (not committed)
├── .env.example                # Template for environment configuration
├── manage.py                   # Django CLI management entrypoint
├── run.sh                      # Shell script to start the local server
│
├── config/                     # Project-level configuration & routing
│   ├── settings/
│   │   ├── base.py             # Shared settings (apps, middleware, Supabase DB & Auth)
│   │   ├── local.py            # Development-specific settings
│   │   └── production.py       # Production hardening settings
│   ├── urls.py                 # Top-level URL routing
│   ├── views.py                # Global views (About page, landing redirects)
│   ├── wsgi.py                 # WSGI application callable
│   └── asgi.py                 # ASGI application callable
│
├── apps/                       # Pluggable Django applications
│   ├── users/                  # User accounts, authentication & roles
│   │   ├── backends.py         # Supabase Auth backend integration
│   │   ├── models.py           # CustomUser model (Student / Coordinator / Teacher)
│   │   ├── views.py            # Login, registration, dashboard routing
│   │   ├── forms.py            # User registration & profile forms
│   │   ├── decorators.py       # Role-based access decorators (@role_required)
│   │   └── urls.py             # User authentication endpoints
│   │
│   ├── events/                 # College event management
│   │   ├── models.py           # Event model & metadata
│   │   ├── views.py            # Event CRUD & listings
│   │   ├── forms.py            # Event creation and editing forms
│   │   └── urls.py             # Event management routes
│   │
│   └── attendance/             # Core attendance request & review pipeline
│       ├── models.py           # AttendanceRequest model with status tracking
│       ├── forms.py            # Request submission & review forms
│       ├── views/              # Modular role-specific view handlers
│       │   ├── student.py      # Student request submission & status tracking
│       │   ├── coordinator.py  # Coordinator event request reviews
│       │   ├── teacher.py      # Final teacher approval & attendance marking
│       │   └── exports.py      # Excel workbook generation (openpyxl)
│       └── urls.py             # Attendance routing
│
├── requirements/               # Environment dependency manifests
│   ├── base.txt                # Core packages (Django, psycopg2, supabase, openpyxl)
│   ├── local.txt               # Local development dependencies
│   └── production.txt          # Production server dependencies (e.g. gunicorn)
│
├── templates/                  # Base templates and layout includes
│   ├── base.html               # Main base layout with glassmorphic styling
│   ├── about.html              # About AttendEase page
│   └── includes/
│       ├── navbar.html         # Navigation bar with user dropdown
│       ├── sidebar.html        # Dynamic role-filtered navigation sidebar
│       └── messages.html       # Toast & alert messages
│
└── static/                     # Static UI assets
    ├── css/style.css           # Custom CSS design system
    └── js/main.js              # Interactive UI scripts (sidebar, ripples, stats)
```

---

## Environment Variables Reference

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Unique Django secret cryptographic key | `django-insecure-...` |
| `DJANGO_DEBUG` | Enable debug mode (`True` for dev, `False` for prod) | `True` |
| `SUPABASE_DB_HOST` | Supabase PostgreSQL server hostname | `db.xxxx.supabase.co` |
| `SUPABASE_DB_PORT` | PostgreSQL connection port | `5432` or `6543` |
| `SUPABASE_DB_NAME` | PostgreSQL database name | `postgres` |
| `SUPABASE_DB_USER` | PostgreSQL username | `postgres` |
| `SUPABASE_DB_PASSWORD` | PostgreSQL database user password | `••••••••` |
| `SUPABASE_URL` | Supabase project API URL | `https://xxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase public anonymous API key | `eyJhbGciOi...` |

---

## Useful Management Commands

```bash
# Check configuration and models
python3 manage.py check

# Create new database migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create an administrator
python3 manage.py createsuperuser

# Change a user password
python3 manage.py changepassword <username>

# Run Django interactive shell
python3 manage.py shell
```

---

## Tech Stack & Dependencies

| Technology | Purpose |
| :--- | :--- |
| **Django 4.2+** | Robust web framework for application backend and ORM |
| **Supabase (PostgreSQL)** | Managed PostgreSQL database storing all models and requests |
| **Supabase Auth / GoTrue** | User identity, authentication, and secure token validation |
| **psycopg2-binary** | PostgreSQL database adapter for Python |
| **openpyxl** | Automated Excel report generation for teacher attendance logs |
| **python-dotenv** | Secure environment variable management via `.env` |
| **HTML5 & Vanilla CSS** | Clean glassmorphic design system without bulky UI frameworks |

---

## License

This project is intended for educational and institutional attendance tracking.
