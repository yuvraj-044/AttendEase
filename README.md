# AttendEase — College Event Attendance Management System

A Django web application that manages the end-to-end workflow for students requesting approval to attend college events, reviewed first by an event coordinator and then by a class teacher.

---

## Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Apply migrations
python3 manage.py migrate

# 3. Start the development server
sh run.sh          # default port 8000
sh run.sh 8001     # custom port
```

Then open **http://127.0.0.1:8000/** in your browser.

> **Port conflict?** Kill the existing process: `lsof -t -i :8000 | xargs kill -9`

---

## Roles

| Role | What they can do |
|------|-----------------|
| **Student** | Submit attendance requests for internal or open (external) events |
| **Event Coordinator** | Create events; approve or reject student requests for their own events |
| **Class Teacher** | Give final approval/rejection; mark actual attendance; export records to Excel |

---

## Approval Workflow

```
Student submits
      │
      ▼
[Coordinator Event]──► Coordinator approves/rejects
      │                         │
      │                         ▼
[Open Event] ─────────► Teacher approves/rejects
                                │
                                ▼
                        Teacher marks attended ✓
```

Open (external) events skip the coordinator step and go directly to the teacher.

---

## Project Structure

```
AttendEase/
│
├── manage.py                   # Django management CLI
├── views.py                    # Project-level views (About page)
├── run.sh                      # Convenience dev-server start script
├── requirements.txt
│
├── config/                     # Django project settings & routing
│   ├── settings.py
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── users/                      # Authentication & role management
│   ├── models.py               # CustomUser (Student / Coordinator / Teacher)
│   ├── views.py                # Login, logout, register, dashboard redirect
│   ├── forms.py                # Registration & login forms
│   ├── admin.py
│   ├── decorators.py           # @role_required access control decorator
│   ├── urls.py
│   ├── apps.py
│   ├── migrations/
│   └── templates/users/
│       ├── login.html
│       └── register.html
│
├── events/                     # Event creation & listing (coordinator-managed)
│   ├── models.py               # Event model
│   ├── views.py                # CRUD views for events
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   ├── apps.py
│   ├── migrations/
│   └── templates/events/
│       ├── event_list.html
│       ├── event_form.html
│       └── event_detail.html
│
├── attendance/                 # Attendance request workflow (core app)
│   ├── models.py               # AttendanceRequest model + approval states
│   ├── forms.py                # Request submission & review forms
│   ├── admin.py
│   ├── urls.py
│   ├── apps.py
│   ├── migrations/
│   ├── views/                  # Split by role for clarity
│   │   ├── __init__.py         # Re-exports all view callables
│   │   ├── student.py          # Dashboard, submit request, request detail
│   │   ├── coordinator.py      # Dashboard, review requests
│   │   ├── teacher.py          # Dashboard, review requests, mark attendance
│   │   └── exports.py          # Excel export for teachers
│   └── templates/attendance/
│       ├── student_dashboard.html
│       ├── coordinator_dashboard.html
│       ├── teacher_dashboard.html
│       ├── submit_request.html
│       ├── review_request.html
│       ├── request_detail.html
│       └── mark_attendance.html
│
├── templates/                  # Project-wide base templates
│   ├── base.html
│   ├── about.html
│   └── includes/
│       ├── navbar.html
│       ├── sidebar.html
│       └── messages.html
│
└── static/
    ├── css/style.css           # Design system (glassmorphic dashboard UI)
    └── js/main.js              # Sidebar toggle, stat counters, ripple effects
```

---

## User Management

Reset a user's password via the CLI:

```bash
python3 manage.py changepassword <username>
```

Create a superuser for full admin access:

```bash
python3 manage.py createsuperuser
```

Admin panel is available at **http://127.0.0.1:8000/admin/**.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `django>=4.2,<5.0` | Web framework |
| `openpyxl>=3.1` | Excel export for teacher attendance records |
